"""
Task model with AI evaluation.
"""
from datetime import date, datetime, time
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .subtask import Subtask
    from .user import User


class Task(Base, UUIDMixin, TimestampMixin):
    """User task with AI-evaluated difficulty and rewards."""
    
    __tablename__ = "tasks"
    
    # Owner
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Basic info
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="general", nullable=False)
    
    # Priority & Deadline
    priority: Mapped[str] = mapped_column(
        String(20), default="medium", nullable=False
    )  # low, medium, high, urgent
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    due_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    
    # AI Evaluation
    ai_difficulty: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # trivial, easy, medium, hard, epic, legendary
    ai_xp_reward: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_coins_reward: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_suggested_subtasks: Mapped[list[Any]] = mapped_column(
        JSONB, default=list, nullable=False
    )
    
    # User adjustments
    user_xp_adjustment: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_coins_adjustment: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Final rewards (AI + adjustments)
    final_xp_reward: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    final_coins_reward: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )  # pending, in_progress, completed, cancelled
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tasks")
    subtasks: Mapped[list["Subtask"]] = relationship(
        "Subtask", back_populates="task", lazy="selectin", cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("idx_tasks_user_id", "user_id"),
        Index("idx_tasks_status", "user_id", "status"),
        Index("idx_tasks_due_date", "due_date", postgresql_where="status = 'pending'"),
    )
    
    def __repr__(self) -> str:
        return f"<Task {self.title} (status={self.status}, difficulty={self.ai_difficulty})>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date or self.status != "pending":
            return False
        return self.due_date < date.today()
    
    def calculate_final_rewards(self) -> None:
        """Calculate final rewards from AI + user adjustments."""
        self.final_xp_reward = (self.ai_xp_reward or 0) + self.user_xp_adjustment
        self.final_coins_reward = (self.ai_coins_reward or 0) + self.user_coins_adjustment
