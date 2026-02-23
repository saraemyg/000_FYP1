"""
Attribute classification service (STUB implementation).

This module provides a stub implementation for pedestrian attribute recognition.
TODO FYP2: Replace with fine-tuned ResNet-50 inference pipeline.
"""
import random
from typing import Any

import numpy as np
from loguru import logger


class AttributeClassifier:
    """Pedestrian attribute classifier using ResNet-50 (STUB)."""

    # Available attribute values
    COLORS = ["red", "blue", "black", "white", "gray", "green", "yellow", "brown", "pink", "orange"]
    GENDERS = ["male", "female", "unknown"]

    def __init__(self) -> None:
        """
        STUB: Initialize with pretrained ResNet-50 model reference.
        TODO FYP2: Load fine-tuned ResNet-50 weights for PAR task.
        """
        self.model_name = "resnet50_par.pth"
        self._initialized = True
        logger.info(f"STUB: Attribute classifier initialized with {self.model_name}")

    def classify_attributes(self, person_crop: np.ndarray) -> dict[str, Any]:
        """
        STUB: Mock attribute classification.
        Returns random attributes with realistic confidence scores.

        Args:
            person_crop: Cropped person image as numpy array

        Returns:
            Dictionary with attribute predictions and confidences
        """
        # Generate realistic mock predictions
        upper_color = random.choice(self.COLORS)
        lower_color = random.choice(self.COLORS)
        gender = random.choices(
            self.GENDERS,
            weights=[0.45, 0.45, 0.10]  # Slight bias away from unknown
        )[0]

        result = {
            "upper_color": upper_color,
            "upper_color_confidence": round(random.uniform(0.65, 0.92), 3),
            "lower_color": lower_color,
            "lower_color_confidence": round(random.uniform(0.65, 0.92), 3),
            "gender": gender,
            "gender_confidence": round(random.uniform(0.70, 0.95), 3),
        }

        logger.debug(f"STUB: Classified attributes - gender={gender}, upper={upper_color}, lower={lower_color}")
        return result

    def classify_batch(self, crops: list[np.ndarray]) -> list[dict[str, Any]]:
        """
        STUB: Batch attribute classification.

        Args:
            crops: List of cropped person images

        Returns:
            List of attribute dictionaries
        """
        return [self.classify_attributes(crop) for crop in crops]


# Global singleton instance
_classifier_instance: AttributeClassifier | None = None


def get_attribute_classifier() -> AttributeClassifier:
    """Get or create the attribute classifier singleton."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = AttributeClassifier()
    return _classifier_instance
