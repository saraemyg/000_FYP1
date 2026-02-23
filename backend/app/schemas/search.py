"""Search schemas for API request/response validation."""
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class NaturalLanguageQuery(BaseModel):
    """Schema for natural language search query."""
    query: str = Field(..., min_length=1, max_length=500)
    min_confidence: float = Field(default=0.6, ge=0, le=1)
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class AdvancedSearchQuery(BaseModel):
    """Schema for advanced structured search query."""
    gender: Optional[str] = Field(None, pattern="^(male|female|unknown)$")
    upper_color: Optional[str] = None
    lower_color: Optional[str] = None
    min_confidence: float = Field(default=0.6, ge=0, le=1)
    video_id: Optional[int] = None
    start_timestamp: Optional[float] = None
    end_timestamp: Optional[float] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="confidence", pattern="^(confidence|timestamp)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class ParsedQuery(BaseModel):
    """Schema for parsed query attributes."""
    gender: Optional[str] = None
    upper_color: Optional[str] = None
    lower_color: Optional[str] = None
    raw_query: str


class SearchResultItem(BaseModel):
    """Schema for individual search result."""
    detection_id: int
    video_id: int
    video_filename: str
    frame_number: int
    timestamp_in_video: float
    bbox_x: int
    bbox_y: int
    bbox_width: int
    bbox_height: int
    detection_confidence: float
    person_crop_path: Optional[str] = None
    upper_color: Optional[str] = None
    upper_color_confidence: Optional[float] = None
    lower_color: Optional[str] = None
    lower_color_confidence: Optional[float] = None
    gender: Optional[str] = None
    gender_confidence: Optional[float] = None
    aggregate_confidence: float


class SearchResponse(BaseModel):
    """Schema for search results response."""
    query: str
    parsed_attributes: ParsedQuery
    total_count: int
    results: list[SearchResultItem]


class SearchHistoryItem(BaseModel):
    """Schema for search history item."""
    search_id: int
    query_text: str
    parsed_attributes: Optional[dict[str, Any]] = None
    result_count: Optional[int] = None
    search_timestamp: datetime

    class Config:
        from_attributes = True
