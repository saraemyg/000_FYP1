"""Camera database model."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.segmentation import SegmentationMask


class Camera(Base):
    """Camera model for surveillance camera configuration."""

    __tablename__ = "cameras"

    camera_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    camera_name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    resolution: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    fps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mask_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    segmentation_masks: Mapped[list["SegmentationMask"]] = relationship(
        "SegmentationMask", back_populates="camera", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Camera {self.camera_name}>"
