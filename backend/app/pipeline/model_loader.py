"""
Model Loader — loads YOLO and behavior classifier ONCE at startup.

Behavior classifier selection (set BEHAVIOR_CLASSIFIER in .env):
    mlp    → BehaviorMLP (custom trained, needs models/behavior_mlp_v1_final.pth)
    stgcn  → STGCN++ (pretrained NTU120, needs models/stgcnpp_ntu120_xsub_hrnet_joint.pth)

Default: stgcn (better accuracy out of the box, no training needed)
"""
import torch
from loguru import logger
from app.core.config import settings

_yolo_model = None
_mlp_model  = None
_classifier = None   # holds STGCNClassifier or BehaviorClassifier instance


def get_yolo_model():
    """Get YOLOv11-Pose model (lazy-loaded on first call)."""
    global _yolo_model
    if _yolo_model is None:
        _yolo_model = _load_yolo()
    return _yolo_model


def get_mlp_model():
    """Get raw MLP nn.Module (lazy-loaded, returns None if not trained yet)."""
    global _mlp_model
    if _mlp_model is None:
        _mlp_model = _load_mlp()
    return _mlp_model


def get_behavior_classifier():
    """
    Get the configured behavior classifier instance (lazy-loaded).
    Returns STGCNClassifier or BehaviorClassifier depending on BEHAVIOR_CLASSIFIER setting.
    """
    global _classifier
    if _classifier is None:
        backend = getattr(settings, "BEHAVIOR_CLASSIFIER", "stgcn").lower()
        if backend == "stgcn":
            from app.pipeline.stgcn_classifier import get_stgcn_classifier
            _classifier = get_stgcn_classifier()
            logger.info("Behavior classifier: STGCN++")
        else:
            from app.pipeline.classifier import BehaviorClassifier
            _classifier = BehaviorClassifier(mlp_model=get_mlp_model())
            logger.info("Behavior classifier: MLP")
    return _classifier


def _load_yolo():
    from ultralytics import YOLO
    import numpy as np

    model_path = getattr(settings, "YOLO_MODEL_PATH", "yolo11n-pose.pt")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    use_half = device == "cuda"

    logger.info(f"Loading YOLO from {model_path} on {device} (half={use_half})")
    model = YOLO(model_path)

    # Warm up
    dummy = np.zeros((640, 640, 3), dtype=np.uint8)
    model.predict(dummy, device=device, half=use_half, verbose=False)
    logger.info("YOLO model loaded and warmed up")
    return model


def _load_mlp():
    import os
    mlp_path = getattr(settings, "MLP_MODEL_PATH", "models/behavior_mlp.pth")
    if not os.path.exists(mlp_path):
        logger.warning(f"MLP not found at {mlp_path} — classification will be skipped (pipeline runs in detection-only mode)")
        return None

    from app.pipeline.classifier import BehaviorMLP
    device = "cuda" if torch.cuda.is_available() else "cpu"
    checkpoint = torch.load(mlp_path, map_location=device, weights_only=False)

    # Support both formats:
    #   Format A (notebook full checkpoint): dict with "model_state_dict" + "config"
    #   Format B (state dict only):          plain OrderedDict from torch.save(model.state_dict())
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
        cfg = checkpoint.get("config", {})
        input_size  = cfg.get("input_size",  51 * 15)
        num_classes = cfg.get("num_classes", 7)
        hidden_sizes = cfg.get("hidden_sizes", [256, 128, 64])
    else:
        # plain state dict — infer sizes from weights
        state_dict   = checkpoint
        input_size   = 51 * 15
        num_classes  = 7
        hidden_sizes = [256, 128, 64]

    model = BehaviorMLP(input_size=input_size, num_classes=num_classes, hidden_sizes=hidden_sizes)
    model.load_state_dict(state_dict)
    model.to(device)
    if device == "cuda":
        model.half()   # FP16 inference on GPU — cuts VRAM and speeds up
    model.eval()
    logger.info(f"MLP classifier loaded: {input_size}→{hidden_sizes}→{num_classes} on {device}")
    return model
