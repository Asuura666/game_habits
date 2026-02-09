"""
Notification model for user alerts.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin

if TYPE_CHECKING:
    from .user import User


class Notification(Base, UUIDMixin):
    """User notification."""
    
    __tablename__ = "notifications"
    
    # Owner
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Content
    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # friend_request, combat_challenge, badge_unlocked, leaderboard_change, streak_warning, etc.
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    
    __table_args__ = (
        Index("idx_notifications_user", "user_id", "is_read"),
        Index("idx_notifications_created", "created_at"),
    )
    
    def __repr__(self) -> str:
        read_status = "✓" if self.is_read else "○"
        return f"<Notification [{read_status}] {self.type}: {self.title[:30]}>"
    
    def mark_as_read(self) -> None:
        """Mark notification as read."""
        self.is_read = True
