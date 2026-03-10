"""
Database Loader (LOAD Stage)
=============================
Saves detection results, keypoints, and behaviors to PostgreSQL.

Uses batch inserts for efficiency — instead of one INSERT per detection,
we collect all results from one frame and insert them together.
"""

import cv2
import logging
import numpy as np
from datetime import datetime
from typing import List, Optional

from db.database import get_db_session
from db.models import Detection, PoseKeypoint, Behavior
from pipeline.detector import PersonDetection
from pipeline.classifier import BehaviorResult
from config import settings

logger = logging.getLogger(__name__)


class DatabaseLoader:
    """
    Saves frame processing results to the database.
    
    Usage:
        loader = DatabaseLoader()
        detection_ids = loader.save_frame_results(
            camera_db_id=1,
            frame_number=42,
            timestamp=datetime.now(),
            detections=[...],
            behaviors=[...],
            frame=original_frame  # for snapshots
        )
    """

    def save_frame_results(
        self,
        camera_db_id: int,
        frame_number: int,
        timestamp: datetime,
        detections: List[PersonDetection],
        behaviors: List[BehaviorResult],
        frame: Optional[np.ndarray] = None,
    ) -> List[int]:
        """
        Save all detections + keypoints + behaviors for one frame.
        
        Returns: List of detection IDs (needed by alert engine).
        """
        if not detections:
            return []

        detection_ids = []

        with get_db_session() as db:
            for det, beh in zip(detections, behaviors):
                # 1. Insert detection record
                detection = Detection(
                    camera_id=camera_db_id,
                    frame_number=frame_number,
                    timestamp=timestamp,
                    person_idx=det.person_idx,
                    bbox_x1=det.bbox[0],
                    bbox_y1=det.bbox[1],
                    bbox_x2=det.bbox[2],
                    bbox_y2=det.bbox[3],
                    confidence=det.confidence,
                )
                db.add(detection)
                db.flush()  # get the auto-generated ID without committing

                # 2. Insert pose keypoints
                if det.keypoints_x and len(det.keypoints_x) == 17:
                    keypoints = PoseKeypoint(
                        detection_id=detection.id,
                        keypoints_x=det.keypoints_x,
                        keypoints_y=det.keypoints_y,
                        keypoints_conf=det.keypoints_conf,
                    )
                    db.add(keypoints)

                # 3. Insert behavior classification
                if beh.behavior_type != "unknown":
                    behavior = Behavior(
                        detection_id=detection.id,
                        behavior_type=beh.behavior_type,
                        confidence=beh.confidence,
                        raw_scores=beh.raw_scores,
                    )
                    db.add(behavior)

                detection_ids.append(detection.id)

            # Commit all at once (batch insert)
            # The context manager handles commit/rollback

        return detection_ids

    @staticmethod
    def encode_frame_snapshot(frame: np.ndarray, quality: int = None) -> bytes:
        """
        Encode a frame as JPEG bytes for alert thumbnails.
        
        Args:
            frame: BGR image (numpy array)
            quality: JPEG quality 0-100 (default from settings)
        
        Returns:
            JPEG bytes
        """
        quality = quality or settings.SNAPSHOT_QUALITY
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        return buffer.tobytes()
