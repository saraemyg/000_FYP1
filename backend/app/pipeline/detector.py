"""Person Detector (TRANSFORM Stage 2) — YOLOv11-Pose real inference."""
import numpy as np
from dataclasses import dataclass, field
from typing import List
from loguru import logger
from app.pipeline.roi_pruner import CropInfo, ROIPruner


@dataclass
class PersonDetection:
    """One detected person in a frame."""
    person_idx: int
    bbox: tuple  # (x1, y1, x2, y2) in original frame coords
    confidence: float
    keypoints_x: List[float] = field(default_factory=list)
    keypoints_y: List[float] = field(default_factory=list)
    keypoints_conf: List[float] = field(default_factory=list)


class PersonDetector:
    """Detects persons and estimates poses using YOLOv11-Pose."""

    def __init__(self, yolo_model, conf_threshold: float = 0.5, iou_threshold: float = 0.45):
        self.model = yolo_model
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

    def detect(self, frame: np.ndarray, crop_info: CropInfo) -> List[PersonDetection]:
        if frame is None or frame.size == 0:
            return []
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        use_half = device == "cuda"

        results = self.model.predict(
            frame, device=device, half=use_half,
            conf=self.conf_threshold, iou=self.iou_threshold,
            classes=[0], verbose=False, max_det=20,
        )
        detections = []
        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue
            boxes = result.boxes.xyxy.cpu().numpy()
            confs = result.boxes.conf.cpu().numpy()
            has_kp = result.keypoints is not None and result.keypoints.xy is not None
            if has_kp:
                kps_xy = result.keypoints.xy.cpu().numpy()
                kps_conf = result.keypoints.conf.cpu().numpy()
            for i in range(len(boxes)):
                bbox_orig = ROIPruner.map_bbox_to_original(tuple(boxes[i].tolist()), crop_info)
                kx, ky, kc = [], [], []
                if has_kp and i < len(kps_xy):
                    kx, ky = ROIPruner.map_keypoints_to_original(
                        kps_xy[i, :, 0].tolist(), kps_xy[i, :, 1].tolist(), crop_info
                    )
                    kc = kps_conf[i].tolist()
                detections.append(PersonDetection(
                    person_idx=i, bbox=bbox_orig, confidence=float(confs[i]),
                    keypoints_x=kx, keypoints_y=ky, keypoints_conf=kc,
                ))
        return detections
