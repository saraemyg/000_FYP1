"""
Segmentation service (STUB implementation).

This module provides a stub implementation for walkable region segmentation.
TODO FYP2: Replace with DeepLabv3+ or similar semantic segmentation model.
"""
import os
from typing import Optional

import numpy as np
from loguru import logger
from PIL import Image

from app.core.config import settings


class SegmentationService:
    """Walkable region segmentation service using DeepLabv3+ (STUB)."""

    def __init__(self) -> None:
        """
        STUB: Initialize with DeepLabv3+ model reference.
        TODO FYP2: Load actual segmentation model for mask generation.
        """
        self.model_name = "deeplabv3_resnet50"
        self._initialized = True
        logger.info(f"STUB: Segmentation service initialized with {self.model_name}")

    def generate_mask(self, frame: np.ndarray) -> tuple[np.ndarray, float]:
        """
        STUB: Generate mock walkable region mask.
        Creates a simple mask representing pedestrian areas.

        Args:
            frame: Input frame as numpy array (H, W, C)

        Returns:
            Tuple of (mask array, reduction percentage)
        """
        height, width = frame.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)

        # Simple rectangular walkable region (bottom 60% of frame, center 70%)
        x_start = int(width * 0.15)
        x_end = int(width * 0.85)
        y_start = int(height * 0.40)
        y_end = height

        mask[y_start:y_end, x_start:x_end] = 255

        # Calculate area reduction
        total_pixels = height * width
        walkable_pixels = np.count_nonzero(mask)
        reduction_pct = ((total_pixels - walkable_pixels) / total_pixels) * 100

        logger.info(f"STUB: Generated mask with {reduction_pct:.1f}% area reduction")
        return mask, round(reduction_pct, 2)

    def save_mask(
        self,
        mask: np.ndarray,
        camera_id: int,
        filename: Optional[str] = None
    ) -> str:
        """
        Save generated mask to file.

        Args:
            mask: Mask array to save
            camera_id: Camera ID for naming
            filename: Optional custom filename

        Returns:
            Path to saved mask file
        """
        if filename is None:
            filename = f"mask_camera_{camera_id}.png"

        mask_dir = os.path.join(settings.UPLOAD_DIR, "masks")
        os.makedirs(mask_dir, exist_ok=True)

        mask_path = os.path.join(mask_dir, filename)
        Image.fromarray(mask).save(mask_path)

        logger.info(f"Saved segmentation mask to {mask_path}")
        return mask_path

    def apply_mask(self, frame: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Apply mask to frame for visualization.

        Args:
            frame: Input frame
            mask: Binary mask

        Returns:
            Frame with mask overlay
        """
        # Create colored overlay
        overlay = frame.copy()
        overlay[mask == 0] = (overlay[mask == 0] * 0.3).astype(np.uint8)  # Darken non-walkable

        return overlay


# Global singleton instance
_segmentation_instance: SegmentationService | None = None


def get_segmentation_service() -> SegmentationService:
    """Get or create the segmentation service singleton."""
    global _segmentation_instance
    if _segmentation_instance is None:
        _segmentation_instance = SegmentationService()
    return _segmentation_instance
