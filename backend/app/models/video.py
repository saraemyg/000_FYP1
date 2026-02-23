"""Video database model."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.detection import Detection
    from app.models.performance import PerformanceMetric


class Video(Base):
    """Video model for uploaded surveillance footage."""

    __tablename__ = "videos"

    video_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    upload_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    resolution: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    total_frames: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    processing_status: Mapped[str] = mapped_column(
        String(20), default="uploaded"
    )  # 'uploaded', 'processing', 'completed', 'failed'
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.user_id"), nullable=True
    )

    # Relationships
    uploader: Mapped[Optional["User"]] = relationship("User", back_populates="videos")
    detections: Mapped[list["Detection"]] = relationship(
        "Detection", back_populates="video", cascade="all, delete-orphan"
    )
    performance_metrics: Mapped[list["PerformanceMetric"]] = relationship(
        "PerformanceMetric", back_populates="video", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Video {self.filename}>"
