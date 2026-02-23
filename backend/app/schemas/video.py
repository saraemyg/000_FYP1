"""Video schemas for API request/response validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VideoBase(BaseModel):
    """Base video schema with common fields."""
    filename: str


class VideoCreate(VideoBase):
    """Schema for creating a video record."""
    file_path: str
    duration_seconds: Optional[float] = None
    fps: Optional[float] = None
    resolution: Optional[str] = None
    total_frames: Optional[int] = None


class VideoUpdate(BaseModel):
    """Schema for updating video information."""
    processing_status: Optional[str] = Field(
        None, pattern="^(uploaded|processing|completed|failed)$"
    )
    duration_seconds: Optional[float] = None
    fps: Optional[float] = None
    resolution: Optional[str] = None
    total_frames: Optional[int] = None


class VideoResponse(VideoBase):
    """Schema for video response."""
    video_id: int
    file_path: str
    upload_timestamp: datetime
    duration_seconds: Optional[float] = None
    fps: Optional[float] = None
    resolution: Optional[str] = None
    total_frames: Optional[int] = None
    processing_status: str
    uploaded_by: Optional[int] = None

    class Config:
        from_attributes = True


class VideoProcessingStatus(BaseModel):
    """Schema for video processing status updates."""
    video_id: int
    status: str
    progress: float = Field(ge=0, le=100)
    current_frame: Optional[int] = None
    total_frames: Optional[int] = None
    detections_count: int = 0
    message: Optional[str] = None
