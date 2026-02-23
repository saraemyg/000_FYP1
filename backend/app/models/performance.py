"""Performance metrics database model."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.video import Video


class PerformanceMetric(Base):
    """Performance metric model for tracking processing statistics."""

    __tablename__ = "performance_metrics"

    metric_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    video_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("videos.video_id"), nullable=True
    )
    avg_fps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_detections: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    processing_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    area_reduction_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    video: Mapped[Optional["Video"]] = relationship(
        "Video", back_populates="performance_metrics"
    )

    def __repr__(self) -> str:
        return f"<PerformanceMetric {self.metric_id}>"
