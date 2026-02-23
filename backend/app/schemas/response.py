"""Generic response schemas."""
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    success: bool = False
    error: str
    detail: Optional[Any] = None
