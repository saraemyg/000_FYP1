"""Alert schemas for API request/response validation.

UR5: Reduced Monitoring Burden - Schemas for alert rule configuration
and triggered alert notifications.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AlertRuleBase(BaseModel):
    """Base schema for alert rules."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    gender: Optional[str] = Field(None, pattern="^(male|female|unknown)$")
    upper_color: Optional[str] = None
    lower_color: Optional[str] = None
    min_confidence: float = Field(default=0.7, ge=0, le=1)
    is_active: bool = True
    notify_on_match: bool = True


class AlertRuleCreate(AlertRuleBase):
    """Schema for creating an alert rule."""
    pass


class AlertRuleUpdate(BaseModel):
    """Schema for updating an alert rule."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    gender: Optional[str] = Field(None, pattern="^(male|female|unknown)$")
    upper_color: Optional[str] = None
    lower_color: Optional[str] = None
    min_confidence: Optional[float] = Field(None, ge=0, le=1)
    is_active: Optional[bool] = None
    notify_on_match: Optional[bool] = None


class AlertRuleResponse(AlertRuleBase):
    """Schema for alert rule response."""
    rule_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TriggeredAlertResponse(BaseModel):
    """Schema for triggered alert response."""
    alert_id: int
    rule_id: int
    rule_name: Optional[str] = None
    detection_id: int
    video_id: int
    video_filename: Optional[str] = None
    matched_attributes: Optional[dict[str, Any]] = None
    confidence_score: Optional[float] = None
    timestamp_in_video: Optional[float] = None
    is_read: bool
    is_acknowledged: bool
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    triggered_at: datetime

    class Config:
        from_attributes = True


class AlertStats(BaseModel):
    """Schema for alert statistics."""
    total_rules: int
    active_rules: int
    total_triggered: int
    unread_alerts: int
    unacknowledged_alerts: int
