"""Segmentation mask database model."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.camera import Camera


class SegmentationMask(Base):
    """Segmentation mask model for walkable area detection."""

    __tablename__ = "segmentation_masks"

    mask_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    camera_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("cameras.camera_id"), nullable=True
    )
    mask_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    reduction_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    generation_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    sample_frame_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    camera: Mapped[Optional["Camera"]] = relationship(
        "Camera", back_populates="segmentation_masks"
    )

    def __repr__(self) -> str:
        return f"<SegmentationMask {self.mask_id}>"
