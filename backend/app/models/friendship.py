"""
Friendship model for social features.
"""
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .user import User


class Friendship(Base, UUIDMixin, TimestampMixin):
    """Friendship relationship between users."""
    
    __tablename__ = "friendships"
    
    # Participants
    requester_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    addressee_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )  # pending, accepted, rejected, blocked
    
    # Relationships
    requester: Mapped["User"] = relationship(
        "User",
        foreign_keys=[requester_id],
        back_populates="sent_friend_requests",
    )
    addressee: Mapped["User"] = relationship(
        "User",
        foreign_keys=[addressee_id],
        back_populates="received_friend_requests",
    )
    
    __table_args__ = (
        UniqueConstraint("requester_id", "addressee_id", name="uq_friendship_pair"),
        CheckConstraint("requester_id != addressee_id", name="ck_not_self_friend"),
        Index("idx_friendships_requester", "requester_id"),
        Index("idx_friendships_addressee", "addressee_id"),
        Index("idx_friendships_status", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<Friendship {self.requester_id} -> {self.addressee_id} ({self.status})>"
    
    def accept(self) -> None:
        """Accept friendship request."""
        self.status = "accepted"
    
    def reject(self) -> None:
        """Reject friendship request."""
        self.status = "rejected"
    
    def block(self) -> None:
        """Block user."""
        self.status = "blocked"
