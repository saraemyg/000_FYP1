"""Detection schemas for API request/response validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Schema for bounding box coordinates."""
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class AttributeBase(BaseModel):
    """Base attribute schema."""
    upper_color: Optional[str] = None
    upper_color_confidence: Optional[float] = Field(None, ge=0, le=1)
    lower_color: Optional[str] = None
    lower_color_confidence: Optional[float] = Field(None, ge=0, le=1)
    gender: Optional[str] = Field(None, pattern="^(male|female|unknown)$")
    gender_confidence: Optional[float] = Field(None, ge=0, le=1)


class AttributeCreate(AttributeBase):
    """Schema for creating attributes."""
    detection_id: int


class AttributeResponse(AttributeBase):
    """Schema for attribute response."""
    attribute_id: int
    detection_id: int
    aggregate_confidence: float
    created_at: datetime

    class Config:
        from_attributes = True


class DetectionBase(BaseModel):
    """Base detection schema."""
    frame_number: int = Field(ge=0)
    timestamp_in_video: float = Field(ge=0)
    bbox_x: int = Field(ge=0)
    bbox_y: int = Field(ge=0)
    bbox_width: int = Field(gt=0)
    bbox_height: int = Field(gt=0)
    detection_confidence: float = Field(ge=0, le=1)


class DetectionCreate(DetectionBase):
    """Schema for creating a detection."""
    video_id: int
    person_crop_path: Optional[str] = None


class DetectionResponse(DetectionBase):
    """Schema for detection response."""
    detection_id: int
    video_id: int
    person_crop_path: Optional[str] = None
    created_at: datetime
    attributes: list[AttributeResponse] = []

    class Config:
        from_attributes = True


class DetectionWithVideo(DetectionResponse):
    """Schema for detection response with video information."""
    video_filename: str
    video_resolution: Optional[str] = None
