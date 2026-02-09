"""
User inventory model.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin

if TYPE_CHECKING:
    from .item import Item
    from .user import User


class UserInventory(Base, UUIDMixin):
    """User's inventory of acquired items."""
    
    __tablename__ = "user_inventory"
    
    # References
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    item_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("items.id"),
        nullable=False,
    )
    
    # Status
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    equipped_slot: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True
    )  # weapon, armor, helmet, accessory, pet
    
    # Timestamp
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="inventory")
    item: Mapped["Item"] = relationship("Item", back_populates="inventories")
    
    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_user_inventory"),
        Index("idx_inventory_user_id", "user_id"),
        Index("idx_inventory_equipped", "user_id", "is_equipped"),
    )
    
    def __repr__(self) -> str:
        equipped = " [E]" if self.is_equipped else ""
        return f"<UserInventory item={self.item_id}{equipped}>"
    
    def equip(self, slot: str) -> None:
        """Equip item to a slot."""
        self.is_equipped = True
        self.equipped_slot = slot
    
    def unequip(self) -> None:
        """Unequip item."""
        self.is_equipped = False
        self.equipped_slot = None
