"""
Model Loader
=============
Loads all AI models into memory ONCE at startup.
Other scripts call get_yolo_model() / get_mlp_model() to use them.

Why load once? Loading a model from disk takes 2-5 seconds.
If you loaded it per frame, you'd never reach 15 FPS.
"""

import torch
import logging
from config import settings

logger = logging.getLogger(__name__)

# Global model references (loaded once, used everywhere)
_yolo_model = None
_mlp_model = None


def get_yolo_model():
    """
    Get the YOLOv11-Pose model. Loads from disk on first call.
    
    Returns: Ultralytics YOLO model object ready for inference.
    """
    global _yolo_model
    if _yolo_model is None:
        _yolo_model = _load_yolo()
    return _yolo_model


def get_mlp_model():
    """
    Get the behavior classification MLP model.
    
    Returns: PyTorch MLP model in eval mode.
    """
    global _mlp_model
    if _mlp_model is None:
        _mlp_model = _load_mlp()
    return _mlp_model


def _load_yolo():
    """Load YOLOv11n-Pose with optimal settings for RTX 5060."""
    try:
        from ultralytics import YOLO

        model = YOLO(settings.YOLO_MODEL_PATH)

        # Warm up the model (first inference is always slow due to CUDA init)
        # This ensures consistent FPS from frame 1
        logger.info(f"Loading YOLO model from {settings.YOLO_MODEL_PATH}")
        logger.info(f"Device: {settings.DEVICE}, Half precision: {settings.USE_HALF_PRECISION}")

        # Run a dummy inference to warm up CUDA
        import numpy as np
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        model.predict(
            dummy,
            device=settings.DEVICE,
            half=settings.USE_HALF_PRECISION,
            verbose=False,
        )

        logger.info("✓ YOLO model loaded and warmed up")
        return model

    except Exception as e:
        logger.error(f"✗ Failed to load YOLO model: {e}")
        raise


def _load_mlp():
    """Load the trained MLP behavior classifier."""
    try:
        import os

        if not os.path.exists(settings.MLP_MODEL_PATH):
            logger.warning(
                f"MLP model not found at {settings.MLP_MODEL_PATH}. "
                "Behavior classification will be skipped until model is trained."
            )
            return None

        # Load the model checkpoint
        checkpoint = torch.load(
            settings.MLP_MODEL_PATH,
            map_location=settings.DEVICE,
            weights_only=True,
        )

        # Reconstruct the MLP architecture
        # This must match the architecture used during training
        from pipeline.classifier import BehaviorMLP

        num_classes = len(settings.BEHAVIOR_CLASSES)
        input_size = checkpoint.get("input_size", 17 * 3 * settings.POSE_WINDOW_SIZE)

        model = BehaviorMLP(input_size=input_size, num_classes=num_classes)
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(settings.DEVICE)
        model.eval()

        logger.info(f"✓ MLP classifier loaded ({num_classes} classes)")
        return model

    except Exception as e:
        logger.error(f"✗ Failed to load MLP model: {e}")
        return None


def unload_models():
    """Free GPU memory by unloading models."""
    global _yolo_model, _mlp_model
    _yolo_model = None
    _mlp_model = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    logger.info("Models unloaded, GPU memory freed")
