"""Pose keypoint database model.

Stores the 17 COCO-format keypoints extracted by YOLOv11-Pose for each detection.
Keypoint order: nose, left_eye, right_eye, left_ear, right_ear,
left_shoulder, right_shoulder, left_elbow, right_elbow,
left_wrist, right_wrist, left_hip, right_hip,
left_knee, right_knee, left_ankle, right_ankle.
"""
from datetime import datetime

from sqlalchemy import ARRAY, DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PoseKeypoint(Base):
    """Pose keypoints for a detected person (17 COCO keypoints)."""

    __tablename__ = "pose_keypoints"

    keypoint_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    detection_id: Mapped[int] = mapped_column(
        ForeignKey("detections.detection_id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    keypoints_x: Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=False)
    keypoints_y: Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=False)
    keypoints_conf: Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationship back to detection
    detection = relationship("Detection", backref="pose_keypoints")

    def __repr__(self) -> str:
        return f"<PoseKeypoint detection={self.detection_id}>"
