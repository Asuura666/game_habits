"""
Subtask model for task breakdown.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin

if TYPE_CHECKING:
    from .task import Task


class Subtask(Base, UUIDMixin):
    """Subtask for breaking down larger tasks."""
    
    __tablename__ = "subtasks"
    
    # Parent task
    task_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Status
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Order
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Relationships
    task: Mapped["Task"] = relationship("Task", back_populates="subtasks")
    
    __table_args__ = (Index("idx_subtasks_task_id", "task_id"),)
    
    def __repr__(self) -> str:
        status = "✓" if self.is_completed else "○"
        return f"<Subtask [{status}] {self.title}>"
    
    def complete(self) -> None:
        """Mark subtask as completed."""
        self.is_completed = True
        self.completed_at = datetime.utcnow()
    
    def uncomplete(self) -> None:
        """Mark subtask as not completed."""
        self.is_completed = False
        self.completed_at = None
