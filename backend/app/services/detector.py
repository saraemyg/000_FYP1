"""
Person detection service (STUB implementation).

This module provides a stub implementation for person detection using YOLOv11.
TODO FYP2: Replace with actual YOLOv11 inference pipeline.
"""
import random
from typing import Any

import numpy as np
from loguru import logger


class DetectorService:
    """Person detection service using YOLOv11 (STUB)."""

    def __init__(self) -> None:
        """
        STUB: Initialize with pretrained YOLOv11 model reference.
        TODO FYP2: Load actual YOLOv11s weights and configure GPU inference.
        """
        self.model_name = "yolov11s.pt"
        self.confidence_threshold = 0.6
        self._initialized = True
        logger.info(f"STUB: Detector initialized with model {self.model_name}")

    def detect_persons(self, frame: np.ndarray) -> list[dict[str, Any]]:
        """
        STUB: Mock person detection.
        Returns random bounding boxes for demonstration.

        Args:
            frame: Input video frame as numpy array (H, W, C)

        Returns:
            List of detection dictionaries with bbox and confidence
        """
        height, width = frame.shape[:2]
        num_detections = random.randint(0, 5)

        detections = []
        for _ in range(num_detections):
            # Generate reasonable bounding box dimensions
            w = random.randint(60, min(150, width // 3))
            h = random.randint(120, min(250, height // 2))
            x = random.randint(0, max(1, width - w))
            y = random.randint(0, max(1, height - h))
            conf = random.uniform(0.65, 0.95)

            if conf >= self.confidence_threshold:
                detections.append({
                    "bbox": [x, y, w, h],
                    "confidence": round(conf, 3),
                })

        logger.debug(f"STUB: Detected {len(detections)} persons in frame")
        return detections

    def detect_batch(self, frames: list[np.ndarray]) -> list[list[dict[str, Any]]]:
        """
        STUB: Batch person detection.

        Args:
            frames: List of video frames

        Returns:
            List of detection results for each frame
        """
        return [self.detect_persons(frame) for frame in frames]

    def set_confidence_threshold(self, threshold: float) -> None:
        """Set the detection confidence threshold."""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Detection confidence threshold set to {self.confidence_threshold}")


# Global singleton instance
_detector_instance: DetectorService | None = None


def get_detector() -> DetectorService:
    """Get or create the detector service singleton."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = DetectorService()
    return _detector_instance
