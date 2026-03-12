"""Pipeline Runner — orchestrates Extract → Transform → Load for one video."""
from datetime import datetime
from loguru import logger

from app.pipeline.extractor import FrameExtractor
from app.pipeline.roi_pruner import ROIPruner
from app.pipeline.detector import PersonDetector
from app.pipeline.loader import DatabaseLoader
from app.pipeline.alert_engine import AlertEngine
from app.pipeline.metrics import MetricsLogger
from app.pipeline.model_loader import get_yolo_model, get_behavior_classifier


class PipelineRunner:
    """Runs the complete ETL pipeline for one video."""

    def __init__(self, camera_id: str, video_path: str, mask_path: str, video_id: int):
        self.camera_id = camera_id
        self.video_id = video_id
        self.extractor  = FrameExtractor(camera_id, video_path)
        self.pruner     = ROIPruner(mask_path)
        self.detector   = PersonDetector(get_yolo_model())
        self.classifier = get_behavior_classifier()   # STGCN++ or MLP based on settings
        self.loader     = DatabaseLoader()
        self.alert_engine = AlertEngine()
        self.metrics    = MetricsLogger(video_id)
        self._processed = 0

    def run(self):
        logger.info(f"{'='*50}")
        logger.info(f"Pipeline starting: {self.camera_id} (video_id={self.video_id})")
        logger.info(f"{'='*50}")

        self.alert_engine.load_rules()
        self.extractor.start()

        try:
            self._loop()
        except KeyboardInterrupt:
            logger.info("Pipeline stopped by user")
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            raise
        finally:
            self.extractor.stop()
            # Flush all pending async DB writes before exit
            self.loader.flush_and_stop()
            logger.info(
                f"Pipeline done. {self._processed} frames, "
                f"{self.metrics.current_fps:.1f} avg FPS"
            )

    def _loop(self):
        while True:
            frame_data = self.extractor.get_frame()
            if frame_data is None:
                break
            self.metrics.frame_start()
            try:
                cropped, crop_info = self.pruner.crop(frame_data.frame)
                detections = self.detector.detect(cropped, crop_info)
                behaviors = self.classifier.classify(detections, self.camera_id)

                # Async DB write — enqueues only, never blocks the inference loop
                self.loader.save_frame_results(
                    video_id=self.video_id,
                    frame_number=frame_data.frame_number,
                    timestamp=frame_data.timestamp,
                    detections=detections,
                    behaviors=behaviors,
                )

                # Alert engine works directly from behavior results (no DB ID required)
                alert_ids = self.alert_engine.evaluate(
                    detections, behaviors, [], self.video_id, frame_data.timestamp
                )
                self._processed += 1
                self.metrics.frame_end(len(detections), len(alert_ids))
            except Exception as e:
                logger.error(f"Frame {frame_data.frame_number} error: {e}")
                continue
