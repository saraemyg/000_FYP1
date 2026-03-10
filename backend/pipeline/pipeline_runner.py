"""
Pipeline Runner
================
Orchestrates the full ETL pipeline for one camera/video.

This connects all the pieces:
  Extractor → ROI Pruner → Detector → Classifier → Loader → Alert Engine

Think of it as the assembly line manager — it doesn't do any processing itself,
it just makes sure each piece passes work to the next.
"""

import logging
import time
from datetime import datetime
from typing import Optional

from db.database import get_db_session
from db.models import Camera, ProcessingSession
from pipeline.extractor import FrameExtractor
from pipeline.roi_pruner import ROIPruner
from pipeline.detector import PersonDetector
from pipeline.classifier import BehaviorClassifier
from pipeline.loader import DatabaseLoader
from pipeline.alert_engine import AlertEngine
from pipeline.metrics_logger import MetricsLogger
from config import settings

logger = logging.getLogger(__name__)


class PipelineRunner:
    """
    Runs the complete ETL pipeline for one camera.
    
    Usage:
        runner = PipelineRunner(
            camera_id="cam_01",
            video_path="data/entrance.mp4",
            mask_path="masks/cam_01_mask.npy",
            camera_db_id=1,
            yolo_model=yolo_model,
            mlp_model=mlp_model,
        )
        runner.run()
    """

    def __init__(
        self,
        camera_id: str,
        video_path: str,
        mask_path: str,
        camera_db_id: int,
        yolo_model,
        mlp_model,
    ):
        self.camera_id = camera_id
        self.camera_db_id = camera_db_id

        # Initialize all pipeline stages
        self.extractor = FrameExtractor(camera_id, video_path)
        self.pruner = ROIPruner(mask_path)
        self.detector = PersonDetector(yolo_model)
        self.classifier = BehaviorClassifier(mlp_model)
        self.loader = DatabaseLoader()
        self.alert_engine = AlertEngine()
        self.metrics = MetricsLogger(camera_db_id)

        # Session tracking
        self._session_id: Optional[int] = None
        self._processed_frames: int = 0

    def run(self):
        """Run the full pipeline end-to-end."""
        logger.info(f"{'='*60}")
        logger.info(f"Starting pipeline for camera: {self.camera_id}")
        logger.info(f"{'='*60}")

        # Create processing session record
        self._start_session()

        # Load alert rules from DB
        self.alert_engine.load_rules()

        # Start frame extraction (background thread)
        self.extractor.start()

        try:
            self._process_loop()
            self._end_session("COMPLETED")
        except KeyboardInterrupt:
            logger.info(f"[{self.camera_id}] Pipeline stopped by user")
            self._end_session("CANCELLED")
        except Exception as e:
            logger.error(f"[{self.camera_id}] Pipeline error: {e}")
            self._end_session("FAILED", str(e))
            raise
        finally:
            self.extractor.stop()

    def _process_loop(self):
        """Main frame-by-frame processing loop."""
        while True:
            # Get next frame from extractor
            frame_data = self.extractor.get_frame()
            if frame_data is None:
                break  # video ended

            self.metrics.frame_start()

            try:
                # ── TRANSFORM Stage 1: ROI Crop ──
                cropped_frame, crop_info = self.pruner.crop(frame_data.frame)

                # ── TRANSFORM Stage 2: Detection + Pose ──
                detections = self.detector.detect(cropped_frame, crop_info)

                # ── TRANSFORM Stage 3: Behavior Classification ──
                behaviors = self.classifier.classify(detections, self.camera_id)

                # ── LOAD: Save to Database ──
                detection_ids = self.loader.save_frame_results(
                    camera_db_id=self.camera_db_id,
                    frame_number=frame_data.frame_number,
                    timestamp=frame_data.timestamp,
                    detections=detections,
                    behaviors=behaviors,
                )

                # ── Alert Generation ──
                snapshot = None
                if detections:
                    snapshot = DatabaseLoader.encode_frame_snapshot(frame_data.frame)

                alert_ids = self.alert_engine.evaluate(
                    detections=detections,
                    behaviors=behaviors,
                    detection_ids=detection_ids,
                    camera_db_id=self.camera_db_id,
                    timestamp=frame_data.timestamp,
                    frame_snapshot=snapshot,
                )

                self._processed_frames += 1
                self.metrics.frame_end(
                    detections_count=len(detections),
                    alerts_count=len(alert_ids),
                )

            except Exception as e:
                logger.error(
                    f"[{self.camera_id}] Error processing frame "
                    f"{frame_data.frame_number}: {e}"
                )
                continue  # skip this frame, continue with next

        logger.info(
            f"[{self.camera_id}] Pipeline complete. "
            f"Processed {self._processed_frames} frames. "
            f"Average FPS: {self.metrics.current_fps:.1f}"
        )

    def _start_session(self):
        """Create a processing session record."""
        try:
            with get_db_session() as db:
                session = ProcessingSession(
                    camera_id=self.camera_db_id,
                    video_path=self.extractor.video_path,
                )
                db.add(session)
                db.flush()
                self._session_id = session.id
        except Exception as e:
            logger.error(f"Failed to create session: {e}")

    def _end_session(self, status: str, error: str = None):
        """Update the processing session with final stats."""
        try:
            with get_db_session() as db:
                session = db.query(ProcessingSession).get(self._session_id)
                if session:
                    session.ended_at = datetime.utcnow()
                    session.total_frames = self.extractor.total_frames
                    session.processed_frames = self._processed_frames
                    session.avg_fps = self.metrics.current_fps
                    session.status = status
                    session.error_message = error
        except Exception as e:
            logger.error(f"Failed to update session: {e}")
