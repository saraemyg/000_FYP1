"""Pydantic schemas package."""
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    Token,
    TokenPayload,
)
from app.schemas.video import (
    VideoBase,
    VideoCreate,
    VideoUpdate,
    VideoResponse,
    VideoProcessingStatus,
)
from app.schemas.detection import (
    BoundingBox,
    AttributeBase,
    AttributeCreate,
    AttributeResponse,
    DetectionBase,
    DetectionCreate,
    DetectionResponse,
    DetectionWithVideo,
)
from app.schemas.search import (
    NaturalLanguageQuery,
    AdvancedSearchQuery,
    ParsedQuery,
    SearchResultItem,
    SearchResponse,
    SearchHistoryItem,
)
from app.schemas.camera import (
    CameraBase,
    CameraCreate,
    CameraUpdate,
    CameraResponse,
    SegmentationMaskResponse,
)
from app.schemas.metrics import (
    MetricsSummary,
    VideoMetrics,
    AttributeDistribution,
    GenderDistribution,
    ColorDistribution,
    MetricsDetail,
)
from app.schemas.response import (
    APIResponse,
    PaginatedResponse,
    ErrorResponse,
)
from app.schemas.alert import (
    AlertRuleBase,
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
    TriggeredAlertResponse,
    AlertStats,
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "Token",
    "TokenPayload",
    # Video
    "VideoBase",
    "VideoCreate",
    "VideoUpdate",
    "VideoResponse",
    "VideoProcessingStatus",
    # Detection
    "BoundingBox",
    "AttributeBase",
    "AttributeCreate",
    "AttributeResponse",
    "DetectionBase",
    "DetectionCreate",
    "DetectionResponse",
    "DetectionWithVideo",
    # Search
    "NaturalLanguageQuery",
    "AdvancedSearchQuery",
    "ParsedQuery",
    "SearchResultItem",
    "SearchResponse",
    "SearchHistoryItem",
    # Camera
    "CameraBase",
    "CameraCreate",
    "CameraUpdate",
    "CameraResponse",
    "SegmentationMaskResponse",
    # Metrics
    "MetricsSummary",
    "VideoMetrics",
    "AttributeDistribution",
    "GenderDistribution",
    "ColorDistribution",
    "MetricsDetail",
    # Response
    "APIResponse",
    "PaginatedResponse",
    "ErrorResponse",
    # Alert
    "AlertRuleBase",
    "AlertRuleCreate",
    "AlertRuleUpdate",
    "AlertRuleResponse",
    "TriggeredAlertResponse",
    "AlertStats",
]
