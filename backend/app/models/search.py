"""Search history database model."""
from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class SearchHistory(Base):
    """Search history model for tracking user search queries."""

    __tablename__ = "search_history"

    search_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.user_id"), nullable=True, index=True
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_attributes: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    result_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    search_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="search_history")

    def __repr__(self) -> str:
        return f"<SearchHistory {self.search_id}>"
