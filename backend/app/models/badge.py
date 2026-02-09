"""
Badge models for achievements.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin

if TYPE_CHECKING:
    from .user import User


class Badge(Base, UUIDMixin):
    """Achievement badge definition."""
    
    __tablename__ = "badges"
    
    # Identity
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Rarity & Rewards
    rarity: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # common, uncommon, rare, epic, legendary, secret, seasonal
    xp_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Conditions
    condition_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # streak, completions, level, time, secret, date, combat_wins, etc.
    condition_value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    # Display
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_seasonal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    user_badges: Mapped[list["UserBadge"]] = relationship(
        "UserBadge", back_populates="badge", lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Badge {self.code} ({self.rarity})>"


class UserBadge(Base):
    """User's unlocked badges."""
    
    __tablename__ = "user_badges"
    
    # Composite primary key
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    badge_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("badges.id"),
        primary_key=True,
    )
    
    # Status
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    is_displayed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    display_position: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # 1, 2, 3 for profile display
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="badges")
    badge: Mapped["Badge"] = relationship("Badge", back_populates="user_badges")
    
    __table_args__ = (Index("idx_user_badges_user_id", "user_id"),)
    
    def __repr__(self) -> str:
        return f"<UserBadge user={self.user_id} badge={self.badge_id}>"
