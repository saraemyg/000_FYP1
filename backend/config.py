"""
Configuration Settings
======================
All system settings in one place. Change values here, not in individual scripts.

For local development, copy .env.example to .env and fill in your values.
"""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Settings:
    # ── Database ──────────────────────────────────────────
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/surveillance_db"
    )

    # ── Redis (for caching + pub/sub alerts) ──────────────
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # ── Model Paths ───────────────────────────────────────
    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", "models/yolo11n-pose.pt")
    MLP_MODEL_PATH: str = os.getenv("MLP_MODEL_PATH", "models/behavior_mlp.pth")
    MASKS_DIR: str = os.getenv("MASKS_DIR", "masks/")

    # ── Processing Settings ───────────────────────────────
    TARGET_FPS: int = 15                    # NFR1: target ≥15 FPS
    YOLO_INPUT_SIZE: int = 640              # YOLOv11-Pose input resolution
    YOLO_CONFIDENCE_THRESHOLD: float = 0.5  # minimum detection confidence
    YOLO_IOU_THRESHOLD: float = 0.45        # NMS IoU threshold
    USE_HALF_PRECISION: bool = True         # FP16 inference (saves VRAM on RTX 5060)
    DEVICE: str = "cuda"                    # 'cuda' for GPU, 'cpu' for CPU

    # ── Behavior Classification ───────────────────────────
    BEHAVIOR_CLASSES: List[str] = field(default_factory=lambda: [
        "walking", "standing", "sitting", "running",
        "bending", "falling", "suspicious"
    ])
    POSE_WINDOW_SIZE: int = 15              # frames of pose history for temporal features
    CLASSIFICATION_CONFIDENCE_THRESHOLD: float = 0.5
    TEMPORAL_SMOOTHING_WINDOW: int = 5      # majority vote over N recent predictions

    # ── Alert Settings ────────────────────────────────────
    ALERT_COOLDOWN_SECONDS: int = 10        # minimum time between alerts for same person+behavior
    SNAPSHOT_QUALITY: int = 80              # JPEG quality for frame snapshots (0-100)

    # ── Metrics Logging ───────────────────────────────────
    METRICS_LOG_INTERVAL: int = 5           # log metrics every N seconds

    # ── Video Processing ──────────────────────────────────
    SUPPORTED_FORMATS: List[str] = field(default_factory=lambda: [".mp4", ".avi", ".mov"])
    FRAME_QUEUE_SIZE: int = 30              # max frames buffered in memory per camera
    CAMERA_CONFIG_PATH: str = "camera_config.json"


settings = Settings()
