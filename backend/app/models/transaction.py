"""
Transaction models for XP and coin audit logs.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin

if TYPE_CHECKING:
    from .user import User


class XPTransaction(Base, UUIDMixin):
    """XP transaction audit log."""
    
    __tablename__ = "xp_transactions"
    
    # Owner
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Transaction details
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # habit, task, combat, badge, streak, daily_bonus
    source_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )  # Reference to habit/task/combat/badge
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="xp_transactions")
    
    __table_args__ = (
        Index("idx_xp_transactions_user", "user_id"),
        Index("idx_xp_transactions_date", "created_at"),
    )
    
    def __repr__(self) -> str:
        sign = "+" if self.amount > 0 else ""
        return f"<XPTransaction {sign}{self.amount} XP ({self.source_type})>"


class CoinTransaction(Base, UUIDMixin):
    """Coin transaction audit log."""
    
    __tablename__ = "coin_transactions"
    
    # Owner
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Transaction details
    amount: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # Positive = gain, Negative = spend
    transaction_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # habit, task, combat, purchase, streak
    reference_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="coin_transactions")
    
    __table_args__ = (
        Index("idx_coin_transactions_user", "user_id"),
        Index("idx_coin_transactions_date", "created_at"),
    )
    
    def __repr__(self) -> str:
        sign = "+" if self.amount > 0 else ""
        return f"<CoinTransaction {sign}{self.amount} coins ({self.transaction_type})>"
