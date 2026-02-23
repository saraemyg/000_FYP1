"""Metrics schemas for API request/response validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MetricsSummary(BaseModel):
    """Schema for overall system metrics summary."""
    total_videos: int
    total_detections: int
    average_fps: float
    average_area_reduction: float
    total_processing_time: float


class VideoMetrics(BaseModel):
    """Schema for per-video metrics."""
    video_id: int
    filename: str
    avg_fps: Optional[float] = None
    total_detections: int
    processing_time_seconds: Optional[float] = None
    area_reduction_percentage: Optional[float] = None
    recorded_at: datetime


class AttributeDistribution(BaseModel):
    """Schema for attribute distribution statistics."""
    attribute_name: str
    values: dict[str, int]  # value -> count mapping


class GenderDistribution(BaseModel):
    """Schema for gender distribution."""
    male: int
    female: int
    unknown: int


class ColorDistribution(BaseModel):
    """Schema for color distribution."""
    color: str
    count: int


class MetricsDetail(BaseModel):
    """Schema for detailed metrics response."""
    summary: MetricsSummary
    gender_distribution: GenderDistribution
    upper_color_distribution: list[ColorDistribution]
    lower_color_distribution: list[ColorDistribution]
