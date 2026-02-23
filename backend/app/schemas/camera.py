"""Camera schemas for API request/response validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CameraBase(BaseModel):
    """Base camera schema with common fields."""
    camera_name: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    resolution: Optional[str] = Field(None, max_length=20)
    fps: Optional[float] = Field(None, ge=0)


class CameraCreate(CameraBase):
    """Schema for creating a camera."""
    pass


class CameraUpdate(BaseModel):
    """Schema for updating camera information."""
    camera_name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    resolution: Optional[str] = Field(None, max_length=20)
    fps: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CameraResponse(CameraBase):
    """Schema for camera response."""
    camera_id: int
    mask_file_path: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SegmentationMaskResponse(BaseModel):
    """Schema for segmentation mask response."""
    mask_id: int
    camera_id: Optional[int] = None
    mask_file_path: str
    reduction_percentage: Optional[float] = None
    generation_timestamp: datetime
    sample_frame_path: Optional[str] = None

    class Config:
        from_attributes = True
