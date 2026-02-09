"""
Item model for shop items.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin

if TYPE_CHECKING:
    from .inventory import UserInventory


class Item(Base, UUIDMixin):
    """Shop item with stats bonuses."""
    
    __tablename__ = "items"
    
    # Basic info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # weapon, armor, helmet, accessory, pet
    
    # Rarity & Price
    rarity: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # common, uncommon, rare, epic, legendary
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Stats bonus
    strength_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    endurance_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    agility_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    intelligence_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    charisma_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Visual
    sprite_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sprite_layer: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Availability
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_limited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    available_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    available_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    inventories: Mapped[list["UserInventory"]] = relationship(
        "UserInventory", back_populates="item", lazy="selectin"
    )
    
    __table_args__ = (
        Index("idx_items_category", "category"),
        Index("idx_items_rarity", "rarity"),
        Index("idx_items_available", "is_available"),
    )
    
    def __repr__(self) -> str:
        return f"<Item {self.name} ({self.rarity} {self.category})>"
    
    @property
    def total_stats_bonus(self) -> int:
        """Calculate total stats bonus."""
        return (
            self.strength_bonus
            + self.endurance_bonus
            + self.agility_bonus
            + self.intelligence_bonus
            + self.charisma_bonus
        )
    
    @property
    def rarity_multiplier(self) -> float:
        """Get rarity multiplier for display."""
        multipliers = {
            "common": 1.0,
            "uncommon": 1.2,
            "rare": 1.5,
            "epic": 2.0,
            "legendary": 3.0,
        }
        return multipliers.get(self.rarity, 1.0)
