"""Detection database model."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.video import Video
    from app.models.attribute import Attribute


class Detection(Base):
    """Detection model for person detections in video frames."""

    __tablename__ = "detections"
    __table_args__ = (
        UniqueConstraint("video_id", "frame_number", "bbox_x", "bbox_y", name="uq_detection_location"),
    )

    detection_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.video_id", ondelete="CASCADE"), nullable=False, index=True
    )
    frame_number: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp_in_video: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    bbox_x: Mapped[int] = mapped_column(Integer, nullable=False)
    bbox_y: Mapped[int] = mapped_column(Integer, nullable=False)
    bbox_width: Mapped[int] = mapped_column(Integer, nullable=False)
    bbox_height: Mapped[int] = mapped_column(Integer, nullable=False)
    detection_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    person_crop_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="detections")
    attributes: Mapped[list["Attribute"]] = relationship(
        "Attribute", back_populates="detection", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Detection {self.detection_id} frame={self.frame_number}>"
