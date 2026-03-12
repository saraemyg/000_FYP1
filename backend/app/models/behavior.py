"""Behavior classification database model.

Stores the MLP-classified behavior label for each detection.
Links to Detection via detection_id.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Behavior(Base):
    """Behavior classification result for a detected person."""

    __tablename__ = "behaviors"

    behavior_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    detection_id: Mapped[int] = mapped_column(
        ForeignKey("detections.detection_id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    behavior_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    raw_scores: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationship back to detection
    detection = relationship("Detection", backref="behavior_result")

    def __repr__(self) -> str:
        return f"<Behavior {self.behavior_type} conf={self.confidence:.2f}>"
