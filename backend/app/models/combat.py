"""
Combat model for PvP battles.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin

if TYPE_CHECKING:
    from .user import User


class Combat(Base, UUIDMixin):
    """PvP combat record."""
    
    __tablename__ = "combats"
    
    # Participants
    challenger_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    defender_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    winner_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    
    # Bet
    bet_coins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Combat log (detailed turn-by-turn)
    combat_log: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, default=list, nullable=False
    )
    
    # Stats snapshot at time of combat
    challenger_stats: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    defender_stats: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    # Results
    challenger_final_hp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    defender_final_hp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_turns: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Rewards
    winner_xp_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    winner_coins_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="completed", nullable=False
    )  # pending, completed, cancelled
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    challenger: Mapped["User"] = relationship(
        "User",
        foreign_keys=[challenger_id],
        back_populates="challenged_combats",
    )
    defender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[defender_id],
        back_populates="defending_combats",
    )
    winner: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[winner_id],
    )
    
    __table_args__ = (
        Index("idx_combats_challenger", "challenger_id"),
        Index("idx_combats_defender", "defender_id"),
        Index("idx_combats_created", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Combat {self.challenger_id} vs {self.defender_id} (winner={self.winner_id})>"
    
    @property
    def is_draw(self) -> bool:
        """Check if combat ended in a draw."""
        return self.status == "completed" and self.winner_id is None
    
    def get_loser_id(self) -> Optional[UUID]:
        """Get the loser's ID."""
        if not self.winner_id:
            return None
        return (
            self.defender_id
            if self.winner_id == self.challenger_id
            else self.challenger_id
        )
