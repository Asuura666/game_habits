"""
Habit model for recurring activities.
"""
from datetime import datetime, time
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .completion import Completion
    from .user import User


class Habit(Base, UUIDMixin, TimestampMixin):
    """Recurring habit with streak tracking."""
    
    __tablename__ = "habits"
    
    # Owner
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Basic info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(50), default="✅", nullable=False)
    color: Mapped[str] = mapped_column(String(20), default="#6366F1", nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="general", nullable=False)
    
    # Frequency
    frequency_type: Mapped[str] = mapped_column(
        String(20), default="daily", nullable=False
    )  # daily, weekly, specific_days, x_per_week
    frequency_days: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), default=list, nullable=False
    )  # 0=Mon, 6=Sun
    frequency_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # for x_per_week
    
    # Goal
    target_value: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # NULL for boolean habits
    unit: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True
    )  # pages, minutes, ml, etc.
    
    # Reminder
    reminder_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Gamification
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    best_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_completions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_xp_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Display order
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Status
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="habits")
    completions: Mapped[list["Completion"]] = relationship(
        "Completion", back_populates="habit", lazy="selectin"
    )
    
    __table_args__ = (
        Index("idx_habits_user_id", "user_id"),
        Index("idx_habits_category", "category"),
        Index("idx_habits_archived", "user_id", "is_archived"),
    )
    
    def __repr__(self) -> str:
        return f"<Habit {self.name} (streak={self.current_streak})>"
    
    @property
    def is_countable(self) -> bool:
        """Check if habit has a target value."""
        return self.target_value is not None
