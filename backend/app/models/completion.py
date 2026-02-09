"""
Completion model for habit check-ins.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin

if TYPE_CHECKING:
    from .habit import Habit
    from .user import User


class Completion(Base, UUIDMixin):
    """Habit check-in record."""
    
    __tablename__ = "completions"
    
    # References
    habit_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("habits.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Completion data
    completed_date: Mapped[date] = mapped_column(Date, nullable=False)
    value: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Rewards earned
    xp_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coins_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    streak_multiplier: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), default=Decimal("1.0"), nullable=False
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    habit: Mapped["Habit"] = relationship("Habit", back_populates="completions")
    user: Mapped["User"] = relationship("User", back_populates="completions")
    
    __table_args__ = (
        UniqueConstraint("habit_id", "completed_date", name="uq_completion_habit_date"),
        Index("idx_completions_habit_id", "habit_id"),
        Index("idx_completions_user_date", "user_id", "completed_date"),
        Index("idx_completions_date", "completed_date"),
    )
    
    def __repr__(self) -> str:
        return f"<Completion habit={self.habit_id} date={self.completed_date} value={self.value}>"
