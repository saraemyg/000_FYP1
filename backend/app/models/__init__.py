"""Database models package."""
from app.models.user import User
from app.models.video import Video
from app.models.detection import Detection
from app.models.attribute import Attribute
from app.models.camera import Camera
from app.models.segmentation import SegmentationMask
from app.models.performance import PerformanceMetric
from app.models.search import SearchHistory
from app.models.alert import AlertRule, TriggeredAlert

__all__ = [
    "User",
    "Video",
    "Detection",
    "Attribute",
    "Camera",
    "SegmentationMask",
    "PerformanceMetric",
    "SearchHistory",
    "AlertRule",
    "TriggeredAlert",
]
