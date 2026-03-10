"""
SQLAlchemy ORM Models
====================
Each class here maps to a PostgreSQL table.
Think of it as: Python class = Database table, class attribute = column.

When you do: Detection(camera_id=1, confidence=0.9)
SQLAlchemy generates: INSERT INTO detections (camera_id, confidence) VALUES (1, 0.9)
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text,
    DateTime, ForeignKey, LargeBinary, CheckConstraint,
    Index, ARRAY
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="security_personnel")
    full_name = Column(String(100))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    alert_criteria = relationship("AlertCriteria", back_populates="creator")

    __table_args__ = (
        CheckConstraint("role IN ('security_personnel', 'admin')"),
    )


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True)
    camera_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    location = Column(String(200))
    video_path = Column(String(500))
    resolution_w = Column(Integer)
    resolution_h = Column(Integer)
    fps = Column(Float, default=30.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    mask = relationship("SegmentationMask", back_populates="camera", uselist=False)
    detections = relationship("Detection", back_populates="camera")
    alerts = relationship("Alert", back_populates="camera")
    metrics = relationship("SystemMetric", back_populates="camera")
    sessions = relationship("ProcessingSession", back_populates="camera")


class SegmentationMask(Base):
    __tablename__ = "segmentation_masks"

    id = Column(Integer, primary_key=True)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, unique=True)
    mask_path = Column(String(500), nullable=False)
    crop_x1 = Column(Integer, nullable=False)
    crop_y1 = Column(Integer, nullable=False)
    crop_x2 = Column(Integer, nullable=False)
    crop_y2 = Column(Integer, nullable=False)
    area_reduction = Column(Float)  # percentage, e.g., 42.5 means 42.5% reduction
    model_name = Column(String(50), default="deeplabv3plus")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    camera = relationship("Camera", back_populates="mask")


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    frame_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    person_idx = Column(Integer, nullable=False)
    bbox_x1 = Column(Float, nullable=False)
    bbox_y1 = Column(Float, nullable=False)
    bbox_x2 = Column(Float, nullable=False)
    bbox_y2 = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    camera = relationship("Camera", back_populates="detections")
    keypoints = relationship("PoseKeypoint", back_populates="detection", uselist=False, cascade="all, delete-orphan")
    behavior = relationship("Behavior", back_populates="detection", uselist=False, cascade="all, delete-orphan")
    alert = relationship("Alert", back_populates="detection", uselist=False)

    __table_args__ = (
        Index("idx_detections_camera_ts", "camera_id", "timestamp"),
        Index("idx_detections_timestamp", "timestamp"),
    )


class PoseKeypoint(Base):
    __tablename__ = "pose_keypoints"

    id = Column(Integer, primary_key=True)
    detection_id = Column(Integer, ForeignKey("detections.id", ondelete="CASCADE"), nullable=False)
    keypoints_x = Column(ARRAY(Float), nullable=False)    # 17 x-coordinates
    keypoints_y = Column(ARRAY(Float), nullable=False)    # 17 y-coordinates
    keypoints_conf = Column(ARRAY(Float), nullable=False)  # 17 confidence scores
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    detection = relationship("Detection", back_populates="keypoints")

    __table_args__ = (
        Index("idx_keypoints_detection", "detection_id"),
    )


class Behavior(Base):
    __tablename__ = "behaviors"

    id = Column(Integer, primary_key=True)
    detection_id = Column(Integer, ForeignKey("detections.id", ondelete="CASCADE"), nullable=False)
    behavior_type = Column(String(30), nullable=False)  # walking, running, standing, etc.
    confidence = Column(Float, nullable=False)
    raw_scores = Column(JSONB)  # full softmax output: {"walking": 0.8, "running": 0.1, ...}
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    detection = relationship("Detection", back_populates="behavior")

    __table_args__ = (
        Index("idx_behaviors_detection", "detection_id"),
        Index("idx_behaviors_type", "behavior_type"),
    )


class AlertCriteria(Base):
    __tablename__ = "alert_criteria"

    id = Column(Integer, primary_key=True)
    behavior_type = Column(String(30), nullable=False)
    min_confidence = Column(Float, nullable=False, default=0.7)
    priority = Column(String(10), nullable=False, default="MEDIUM")
    is_enabled = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="alert_criteria")
    alerts = relationship("Alert", back_populates="criteria")

    __table_args__ = (
        CheckConstraint("priority IN ('LOW', 'MEDIUM', 'HIGH')"),
    )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    detection_id = Column(Integer, ForeignKey("detections.id"), nullable=False)
    criteria_id = Column(Integer, ForeignKey("alert_criteria.id"), nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    behavior_type = Column(String(30), nullable=False)
    confidence = Column(Float, nullable=False)
    priority = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    frame_snapshot = Column(LargeBinary)  # JPEG bytes of the alert frame
    timestamp = Column(DateTime, nullable=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id"))
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    detection = relationship("Detection", back_populates="alert")
    criteria = relationship("AlertCriteria", back_populates="alerts")
    camera = relationship("Camera", back_populates="alerts")

    __table_args__ = (
        CheckConstraint("priority IN ('LOW', 'MEDIUM', 'HIGH')"),
        CheckConstraint("status IN ('PENDING', 'ACKNOWLEDGED', 'RESOLVED', 'FALSE_POSITIVE')"),
        Index("idx_alerts_camera_ts", "camera_id", "timestamp"),
        Index("idx_alerts_status", "status"),
        Index("idx_alerts_priority", "priority"),
        Index("idx_alerts_behavior", "behavior_type"),
        Index("idx_alerts_timestamp", "timestamp"),
    )


class SystemMetric(Base):
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    fps = Column(Float)
    avg_latency_ms = Column(Float)
    gpu_util = Column(Float)
    gpu_memory_mb = Column(Float)
    cpu_util = Column(Float)
    detections_count = Column(Integer)
    alerts_count = Column(Integer)
    pipeline_status = Column(String(20), default="RUNNING")
    error_message = Column(Text)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    camera = relationship("Camera", back_populates="metrics")

    __table_args__ = (
        CheckConstraint("pipeline_status IN ('RUNNING', 'PAUSED', 'ERROR', 'STOPPED')"),
        Index("idx_metrics_camera_ts", "camera_id", "recorded_at"),
    )


class ProcessingSession(Base):
    __tablename__ = "processing_sessions"

    id = Column(Integer, primary_key=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    video_path = Column(String(500))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    total_frames = Column(Integer, default=0)
    processed_frames = Column(Integer, default=0)
    avg_fps = Column(Float)
    status = Column(String(20), default="RUNNING")
    error_message = Column(Text)

    # Relationships
    camera = relationship("Camera", back_populates="sessions")

    __table_args__ = (
        CheckConstraint("status IN ('RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')"),
    )
