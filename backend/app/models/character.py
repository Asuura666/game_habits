"""
Character model for RPG elements.
"""
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .user import User


class Character(Base, UUIDMixin, TimestampMixin):
    """RPG Character with stats and appearance (LPC-based)."""
    
    __tablename__ = "characters"
    
    # Owner
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    
    # Identity
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    character_class: Mapped[str] = mapped_column(
        "class", String(20), nullable=False
    )  # warrior, mage, ranger, paladin, assassin
    
    # Appearance (LPC layers)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    skin_color: Mapped[str] = mapped_column(String(20), nullable=False)
    hair_style: Mapped[str] = mapped_column(String(50), nullable=False)
    hair_color: Mapped[str] = mapped_column(String(20), nullable=False)
    eye_color: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Stats
    strength: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    endurance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    agility: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    intelligence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    charisma: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unallocated_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Equipped items (references to inventory)
    equipped_weapon_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    equipped_armor_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    equipped_helmet_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    equipped_accessory_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    equipped_pet_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="character")
    
    def __repr__(self) -> str:
        return f"<Character {self.name} ({self.character_class})>"
    
    @property
    def total_stats(self) -> dict[str, int]:
        """Calculate total stats including equipment bonuses."""
        return {
            "strength": self.strength,
            "endurance": self.endurance,
            "agility": self.agility,
            "intelligence": self.intelligence,
            "charisma": self.charisma,
        }
    
    @property
    def combat_power(self) -> int:
        """Calculate combat power for matchmaking."""
        return (
            self.strength * 2
            + self.endurance * 1.5
            + self.agility * 1.5
            + self.intelligence * 1
            + self.charisma * 0.5
        ).__int__()
