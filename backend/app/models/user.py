"""
User model with gamification features.
"""
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .badge import UserBadge
    from .character import Character
    from .combat import Combat
    from .completion import Completion
    from .friendship import Friendship
    from .habit import Habit
    from .inventory import UserInventory
    from .notification import Notification
    from .task import Task
    from .transaction import CoinTransaction, XPTransaction


class User(Base, UUIDMixin, TimestampMixin):
    """User model with gamification fields."""
    
    __tablename__ = "users"
    
    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Profile
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String(280), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    
    # Gamification
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Streaks
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    best_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_activity_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    streak_freeze_available: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Social
    friend_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # OAuth
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    apple_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    
    # Settings
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    theme: Mapped[str] = mapped_column(String(20), default="dark", nullable=False)
    
    # Login tracking
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Relationships
    character: Mapped[Optional["Character"]] = relationship(
        "Character", back_populates="user", uselist=False, lazy="selectin"
    )
    habits: Mapped[list["Habit"]] = relationship(
        "Habit", back_populates="user", lazy="selectin"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="user", lazy="selectin"
    )
    completions: Mapped[list["Completion"]] = relationship(
        "Completion", back_populates="user", lazy="selectin"
    )
    inventory: Mapped[list["UserInventory"]] = relationship(
        "UserInventory", back_populates="user", lazy="selectin"
    )
    badges: Mapped[list["UserBadge"]] = relationship(
        "UserBadge", back_populates="user", lazy="selectin"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user", lazy="selectin"
    )
    xp_transactions: Mapped[list["XPTransaction"]] = relationship(
        "XPTransaction", back_populates="user", lazy="selectin"
    )
    coin_transactions: Mapped[list["CoinTransaction"]] = relationship(
        "CoinTransaction", back_populates="user", lazy="selectin"
    )
    
    # Friendships (bidirectional)
    sent_friend_requests: Mapped[list["Friendship"]] = relationship(
        "Friendship",
        foreign_keys="Friendship.requester_id",
        back_populates="requester",
        lazy="selectin",
    )
    received_friend_requests: Mapped[list["Friendship"]] = relationship(
        "Friendship",
        foreign_keys="Friendship.addressee_id",
        back_populates="addressee",
        lazy="selectin",
    )
    
    # Combats
    challenged_combats: Mapped[list["Combat"]] = relationship(
        "Combat",
        foreign_keys="Combat.challenger_id",
        back_populates="challenger",
        lazy="selectin",
    )
    defending_combats: Mapped[list["Combat"]] = relationship(
        "Combat",
        foreign_keys="Combat.defender_id",
        back_populates="defender",
        lazy="selectin",
    )
    
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
        Index("idx_users_friend_code", "friend_code"),
        Index("idx_users_google_id", "google_id", postgresql_where=google_id.isnot(None)),
    )
    
    def __repr__(self) -> str:
        return f"<User {self.username} (level={self.level}, xp={self.total_xp})>"
    
    @property
    def is_active(self) -> bool:
        """Check if user account is active (not deleted)."""
        return self.deleted_at is None
