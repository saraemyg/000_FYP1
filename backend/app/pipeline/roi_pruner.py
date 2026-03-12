"""ROI Pruner (TRANSFORM Stage 1) — crops frames to walkable area."""
import numpy as np
import os
from dataclasses import dataclass
from typing import Optional, Tuple
from loguru import logger


@dataclass
class CropInfo:
    x1: int
    y1: int
    x2: int
    y2: int
    original_w: int
    original_h: int
    area_reduction: float


class ROIPruner:
    """Crops frames to the Region of Interest using pre-computed segmentation masks."""

    def __init__(self, mask_path: str):
        self.crop_info: Optional[CropInfo] = None
        if mask_path and os.path.exists(mask_path):
            self._load_mask(mask_path)
        else:
            logger.warning(f"Mask not found: {mask_path}. Full frame mode.")

    def _load_mask(self, mask_path: str):
        mask = np.load(mask_path)
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        if not rows.any() or not cols.any():
            logger.error(f"Mask has no walkable pixels: {mask_path}")
            return
        y1, y2 = np.where(rows)[0][[0, -1]]
        x1, x2 = np.where(cols)[0][[0, -1]]
        h, w = mask.shape
        pad_x, pad_y = int(w * 0.02), int(h * 0.02)
        x1, y1 = max(0, x1 - pad_x), max(0, y1 - pad_y)
        x2, y2 = min(w, x2 + pad_x), min(h, y2 + pad_y)
        reduction = (1 - (y2 - y1) * (x2 - x1) / (h * w)) * 100
        self.crop_info = CropInfo(x1=x1, y1=y1, x2=x2, y2=y2, original_w=w, original_h=h, area_reduction=reduction)
        logger.info(f"ROI crop: ({x1},{y1})-({x2},{y2}) | {reduction:.1f}% area reduction")

    def crop(self, frame: np.ndarray) -> Tuple[np.ndarray, CropInfo]:
        if self.crop_info is None:
            h, w = frame.shape[:2]
            return frame, CropInfo(x1=0, y1=0, x2=w, y2=h, original_w=w, original_h=h, area_reduction=0.0)
        ci = self.crop_info
        return frame[ci.y1:ci.y2, ci.x1:ci.x2], ci

    @staticmethod
    def map_bbox_to_original(bbox: Tuple, ci: CropInfo) -> Tuple:
        return (bbox[0] + ci.x1, bbox[1] + ci.y1, bbox[2] + ci.x1, bbox[3] + ci.y1)

    @staticmethod
    def map_keypoints_to_original(kx: list, ky: list, ci: CropInfo) -> Tuple[list, list]:
        return ([x + ci.x1 for x in kx], [y + ci.y1 for y in ky])
