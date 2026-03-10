"""
Person Detector (TRANSFORM Stage 2)
=====================================
Runs YOLOv11n-Pose on cropped frames to detect people and estimate poses.

Input: Cropped frame from ROI Pruner
Output: List of PersonDetection objects (bbox + 17 keypoints per person)

Key optimizations for RTX 5060 (8GB VRAM):
- FP16 (half precision) inference: halves VRAM usage, ~20% faster
- Single forward pass: detection + pose estimation in ONE model call
- No batch stacking: process one frame at a time to minimize latency
"""

import numpy as np
import logging
from dataclasses import dataclass, field
from typing import List, Optional

from config import settings
from pipeline.roi_pruner import CropInfo, ROIPruner

logger = logging.getLogger(__name__)


@dataclass
class PersonDetection:
    """One detected person in a frame."""
    person_idx: int                    # index within this frame (0, 1, 2...)
    bbox: tuple                        # (x1, y1, x2, y2) in ORIGINAL frame coords
    confidence: float                  # YOLO detection confidence
    keypoints_x: List[float] = field(default_factory=list)   # 17 x-coords (original frame)
    keypoints_y: List[float] = field(default_factory=list)   # 17 y-coords (original frame)
    keypoints_conf: List[float] = field(default_factory=list) # 17 confidence scores


class PersonDetector:
    """
    Detects persons and estimates 17-keypoint poses using YOLOv11-Pose.
    
    Usage:
        detector = PersonDetector(yolo_model)
        detections = detector.detect(cropped_frame, crop_info)
        # detections is a list of PersonDetection objects
    """

    def __init__(self, yolo_model):
        self.model = yolo_model
        self.conf_threshold = settings.YOLO_CONFIDENCE_THRESHOLD
        self.iou_threshold = settings.YOLO_IOU_THRESHOLD

    def detect(self, frame: np.ndarray, crop_info: CropInfo) -> List[PersonDetection]:
        """
        Run YOLO inference on a frame.
        
        Args:
            frame: Cropped frame (from ROI pruner)
            crop_info: Crop offset info for coordinate mapping
        
        Returns:
            List of PersonDetection with coordinates in ORIGINAL frame space
        """
        if frame is None or frame.size == 0:
            return []

        # Run YOLO inference
        results = self.model.predict(
            frame,
            device=settings.DEVICE,
            half=settings.USE_HALF_PRECISION,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            classes=[0],       # class 0 = person in COCO
            verbose=False,
            max_det=20,        # max 20 people per frame (reasonable for surveillance)
        )

        detections = []

        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue

            boxes = result.boxes.xyxy.cpu().numpy()       # (N, 4)
            confs = result.boxes.conf.cpu().numpy()        # (N,)

            # Get keypoints if available
            has_keypoints = result.keypoints is not None and result.keypoints.xy is not None
            if has_keypoints:
                kps_xy = result.keypoints.xy.cpu().numpy()      # (N, 17, 2)
                kps_conf = result.keypoints.conf.cpu().numpy()   # (N, 17)

            for i in range(len(boxes)):
                # Map bounding box back to original frame coordinates
                bbox_original = ROIPruner.map_bbox_to_original(
                    tuple(boxes[i].tolist()), crop_info
                )

                kx, ky, kc = [], [], []
                if has_keypoints and i < len(kps_xy):
                    kx_crop = kps_xy[i, :, 0].tolist()
                    ky_crop = kps_xy[i, :, 1].tolist()
                    kc = kps_conf[i].tolist()

                    # Map keypoints back to original frame
                    kx, ky = ROIPruner.map_keypoints_to_original(
                        kx_crop, ky_crop, crop_info
                    )

                detections.append(PersonDetection(
                    person_idx=i,
                    bbox=bbox_original,
                    confidence=float(confs[i]),
                    keypoints_x=kx,
                    keypoints_y=ky,
                    keypoints_conf=kc,
                ))

        return detections
