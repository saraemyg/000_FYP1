"""Alert model for detection notifications.

UR5: Reduced Monitoring Burden - Enables automated detection alerts
based on configurable attribute conditions.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class AlertRule(Base):
    """Alert rule configuration for automated detection notifications."""

    __tablename__ = "alert_rules"

    rule_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    # Attribute filters (any matching detection triggers alert)
    gender = Column(String(20), nullable=True)
    upper_color = Column(String(50), nullable=True)
    lower_color = Column(String(50), nullable=True)
    min_confidence = Column(Float, default=0.7)

    # Alert settings
    is_active = Column(Boolean, default=True)
    notify_on_match = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="alert_rules")
    triggered_alerts = relationship("TriggeredAlert", back_populates="rule", cascade="all, delete-orphan")


class TriggeredAlert(Base):
    """Record of alerts triggered by matching detections."""

    __tablename__ = "triggered_alerts"

    alert_id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.rule_id", ondelete="CASCADE"), nullable=False)
    detection_id = Column(Integer, ForeignKey("detections.detection_id", ondelete="CASCADE"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.video_id", ondelete="CASCADE"), nullable=False)

    # Alert details
    matched_attributes = Column(JSON, nullable=True)  # What attributes triggered the alert
    confidence_score = Column(Float, nullable=True)
    timestamp_in_video = Column(Float, nullable=True)

    # Status
    is_read = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)

    # Timestamps
    triggered_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    rule = relationship("AlertRule", back_populates="triggered_alerts")
    detection = relationship("Detection", backref="alerts")
    video = relationship("Video", backref="alerts")
