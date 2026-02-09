"""
Daily stats model for aggregated performance data.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDMixin

if TYPE_CHECKING:
    pass


class DailyStats(Base, UUIDMixin):
    """Aggregated daily statistics for performance."""
    
    __tablename__ = "daily_stats"
    
    # Owner
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Date
    date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Habits
    habits_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    habits_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0"), nullable=False
    )
    
    # Tasks
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # XP & Coins
    xp_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coins_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coins_spent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Combat
    combats_won: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    combats_lost: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_daily_stats_user_date"),
        Index("idx_daily_stats_user_date", "user_id", "date"),
    )
    
    def __repr__(self) -> str:
        return f"<DailyStats {self.date} completion={self.completion_rate}%>"
    
    def calculate_completion_rate(self) -> None:
        """Calculate completion rate from totals."""
        if self.habits_total > 0:
            self.completion_rate = Decimal(
                (self.habits_completed / self.habits_total) * 100
            ).quantize(Decimal("0.01"))
        else:
            self.completion_rate = Decimal("0")


class RateLimit(Base):
    """Rate limit tracking for LLM calls."""
    
    __tablename__ = "rate_limits"
    
    # Composite primary key
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    limit_type: Mapped[str] = mapped_column(
        String(30), primary_key=True
    )  # llm_evaluation, task_xp
    
    # Tracking
    current_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<RateLimit {self.limit_type}: {self.current_count}>"
    
    def is_exceeded(self, max_count: int) -> bool:
        """Check if rate limit is exceeded."""
        return self.current_count >= max_count
    
    def increment(self) -> None:
        """Increment the counter."""
        self.current_count += 1
    
    def reset(self, new_reset_at: datetime) -> None:
        """Reset the counter."""
        self.current_count = 0
        self.reset_at = new_reset_at
