"""
ROI Pruner (TRANSFORM Stage 1)
===============================
Crops frames to only the walkable area using pre-computed segmentation masks.

WHY THIS EXISTS (the FPS optimization):
- Without cropping: YOLO processes the FULL frame (e.g., 1920x1080)
- With cropping: YOLO processes only the walkable area (e.g., 1200x700)
- Smaller input = faster inference = higher FPS

HOW IT WORKS:
1. At startup: Load the binary mask (.npy file) for this camera
2. At startup: Find the bounding rectangle of all walkable (white) pixels
3. Per frame: Crop to that rectangle (simple array slice, ~0ms cost)
4. Return cropped frame + offset so coordinates can be mapped back later

WHY CROP, NOT MASK:
- Masking (bitwise AND) still processes the full resolution image
- Cropping physically makes the image smaller → less data for YOLO
- Crop is a numpy slice operation: frame[y1:y2, x1:x2] — essentially free
"""

import numpy as np
import logging
import os
from dataclasses import dataclass
from typing import Optional, Tuple

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class CropInfo:
    """Stores the crop region so we can map coordinates back to original frame."""
    x1: int    # crop region top-left x
    y1: int    # crop region top-left y
    x2: int    # crop region bottom-right x
    y2: int    # crop region bottom-right y
    original_w: int  # original frame width
    original_h: int  # original frame height
    area_reduction: float  # percentage of area removed


class ROIPruner:
    """
    Crops video frames to the Region of Interest (walkable area).
    
    Usage:
        pruner = ROIPruner("masks/cam_01_mask.npy")
        cropped_frame, crop_info = pruner.crop(frame)
        # ... process cropped_frame with YOLO ...
        # ... map bounding boxes back using crop_info ...
    """

    def __init__(self, mask_path: str):
        self.mask_path = mask_path
        self.crop_info: Optional[CropInfo] = None
        self._mask: Optional[np.ndarray] = None

        if mask_path and os.path.exists(mask_path):
            self._load_mask(mask_path)
        else:
            logger.warning(f"Mask not found at {mask_path}. ROI pruning disabled (full frame mode).")

    def _load_mask(self, mask_path: str):
        """
        Load binary mask and compute the bounding rectangle.
        This runs ONCE at startup, not per frame.
        """
        self._mask = np.load(mask_path)  # shape: (H, W), values: 0 or 1

        # Find bounding rectangle of all walkable (white=1) pixels
        rows = np.any(self._mask, axis=1)
        cols = np.any(self._mask, axis=0)

        if not rows.any() or not cols.any():
            logger.error(f"Mask at {mask_path} has no walkable pixels!")
            return

        y1, y2 = np.where(rows)[0][[0, -1]]
        x1, x2 = np.where(cols)[0][[0, -1]]

        # Add small padding (5% each side) to avoid cutting off edge detections
        h, w = self._mask.shape
        pad_x = int(w * 0.02)
        pad_y = int(h * 0.02)
        x1 = max(0, x1 - pad_x)
        y1 = max(0, y1 - pad_y)
        x2 = min(w, x2 + pad_x)
        y2 = min(h, y2 + pad_y)

        # Calculate area reduction percentage
        original_area = h * w
        crop_area = (y2 - y1) * (x2 - x1)
        area_reduction = (1 - crop_area / original_area) * 100

        self.crop_info = CropInfo(
            x1=x1, y1=y1, x2=x2, y2=y2,
            original_w=w, original_h=h,
            area_reduction=area_reduction,
        )

        logger.info(
            f"ROI crop region: ({x1},{y1}) to ({x2},{y2}) | "
            f"Area reduction: {area_reduction:.1f}% | "
            f"{'✓ Meets ≥40% target' if area_reduction >= 40 else '⚠ Below 40% target'}"
        )

    def crop(self, frame: np.ndarray) -> Tuple[np.ndarray, CropInfo]:
        """
        Crop frame to ROI bounding rectangle.
        
        Args:
            frame: Original frame (H x W x 3)
        
        Returns:
            (cropped_frame, crop_info) — cropped_frame is physically smaller
        """
        if self.crop_info is None:
            # No mask loaded — return full frame
            h, w = frame.shape[:2]
            return frame, CropInfo(x1=0, y1=0, x2=w, y2=h, original_w=w, original_h=h, area_reduction=0.0)

        ci = self.crop_info
        cropped = frame[ci.y1:ci.y2, ci.x1:ci.x2]
        return cropped, ci

    @staticmethod
    def map_bbox_to_original(bbox: Tuple[float, float, float, float], crop_info: CropInfo) -> Tuple[float, float, float, float]:
        """
        Map bounding box coordinates from cropped frame back to original frame.
        
        Args:
            bbox: (x1, y1, x2, y2) in cropped frame coordinates
            crop_info: the crop offset info
        
        Returns:
            (x1, y1, x2, y2) in original frame coordinates
        """
        return (
            bbox[0] + crop_info.x1,
            bbox[1] + crop_info.y1,
            bbox[2] + crop_info.x1,
            bbox[3] + crop_info.y1,
        )

    @staticmethod
    def map_keypoints_to_original(
        kps_x: list, kps_y: list, crop_info: CropInfo
    ) -> Tuple[list, list]:
        """Map keypoint coordinates from cropped back to original frame."""
        return (
            [x + crop_info.x1 for x in kps_x],
            [y + crop_info.y1 for y in kps_y],
        )
