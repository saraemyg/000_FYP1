"""Database Loader (LOAD stage) — saves results using existing app/db/session.

FPS optimization: DB writes are queued into a background thread so the
inference loop never waits on Postgres. The queue is flushed every
FLUSH_INTERVAL frames or when it reaches FLUSH_BATCH_SIZE items.
"""
import cv2
import queue
import threading
import numpy as np
from datetime import datetime
from typing import List
from loguru import logger

from app.db.session import SessionLocal
from app.models.detection import Detection
from app.models.pose_keypoint import PoseKeypoint
from app.models.behavior import Behavior
from app.pipeline.detector import PersonDetection
from app.pipeline.classifier import BehaviorResult

FLUSH_BATCH_SIZE = 30   # write to DB every N detection rows
_SENTINEL = None        # queue poison pill


class DatabaseLoader:
    """
    Saves frame processing results to PostgreSQL in a background writer thread.
    The inference loop calls save_frame_results() which only enqueues work —
    it never blocks on I/O, keeping the GPU pipeline at full speed.
    """

    def __init__(self):
        self._queue: queue.Queue = queue.Queue(maxsize=500)
        self._writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self._writer_thread.start()
        self._pending_ids: dict = {}   # frame_number → [detection_id, ...]

    # ── Public API ────────────────────────────────────────────────────────────

    def save_frame_results(
        self,
        video_id: int,
        frame_number: int,
        timestamp: datetime,
        detections: List[PersonDetection],
        behaviors: List[BehaviorResult],
    ) -> List[int]:
        """
        Enqueue frame results for async DB write.
        Returns empty list immediately (IDs are not available yet — alert engine
        works from behaviors directly, not DB IDs, so this is fine).
        """
        if not detections:
            return []
        self._queue.put({
            "video_id": video_id,
            "frame_number": frame_number,
            "timestamp": timestamp,
            "detections": detections,
            "behaviors": behaviors,
        })
        return []

    def flush_and_stop(self):
        """Block until all queued writes are flushed, then stop the writer."""
        self._queue.put(_SENTINEL)
        self._writer_thread.join(timeout=30)

    # ── Background writer ─────────────────────────────────────────────────────

    def _writer_loop(self):
        batch = []
        while True:
            try:
                item = self._queue.get(timeout=2.0)
            except queue.Empty:
                if batch:
                    self._flush(batch)
                    batch = []
                continue

            if item is _SENTINEL:
                if batch:
                    self._flush(batch)
                break

            batch.append(item)
            if len(batch) >= FLUSH_BATCH_SIZE:
                self._flush(batch)
                batch = []

    def _flush(self, batch: list):
        db = SessionLocal()
        try:
            for item in batch:
                video_id     = item["video_id"]
                frame_number = item["frame_number"]
                detections   = item["detections"]
                behaviors    = item["behaviors"]

                for det, beh in zip(detections, behaviors):
                    detection = Detection(
                        video_id=video_id,
                        frame_number=frame_number,
                        timestamp_in_video=0.0,
                        bbox_x=int(det.bbox[0]),
                        bbox_y=int(det.bbox[1]),
                        bbox_width=int(det.bbox[2] - det.bbox[0]),
                        bbox_height=int(det.bbox[3] - det.bbox[1]),
                        detection_confidence=det.confidence,
                    )
                    db.add(detection)
                    db.flush()

                    if det.keypoints_x and len(det.keypoints_x) == 17:
                        db.add(PoseKeypoint(
                            detection_id=detection.detection_id,
                            keypoints_x=det.keypoints_x,
                            keypoints_y=det.keypoints_y,
                            keypoints_conf=det.keypoints_conf,
                        ))

                    if beh.behavior_type != "unknown":
                        db.add(Behavior(
                            detection_id=detection.detection_id,
                            behavior_type=beh.behavior_type,
                            confidence=beh.confidence,
                            raw_scores=beh.raw_scores,
                        ))

            db.commit()
            logger.debug(f"DB flushed {len(batch)} frames")
        except Exception as e:
            db.rollback()
            logger.error(f"DB flush error: {e}")
        finally:
            db.close()

    @staticmethod
    def encode_snapshot(frame: np.ndarray, quality: int = 80) -> bytes:
        _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        return buf.tobytes()
