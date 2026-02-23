"""Attribute database model."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.detection import Detection


class Attribute(Base):
    """Attribute model for person attribute classification results."""

    __tablename__ = "attributes"

    attribute_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    detection_id: Mapped[int] = mapped_column(
        ForeignKey("detections.detection_id", ondelete="CASCADE"), nullable=False, index=True
    )
    upper_color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    upper_color_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lower_color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    lower_color_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)  # 'male', 'female', 'unknown'
    gender_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    detection: Mapped["Detection"] = relationship("Detection", back_populates="attributes")

    @property
    def aggregate_confidence(self) -> float:
        """Calculate aggregate confidence across all attributes."""
        confidences = [
            c for c in [
                self.upper_color_confidence,
                self.lower_color_confidence,
                self.gender_confidence
            ] if c is not None
        ]
        if not confidences:
            return 0.0
        return sum(confidences) / len(confidences)

    def __repr__(self) -> str:
        return f"<Attribute {self.attribute_id} gender={self.gender}>"
