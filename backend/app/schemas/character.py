"""Character schemas for RPG character management."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ClassEnum(str, Enum):
    """Available character classes with unique bonuses."""
    
    WARRIOR = "warrior"      # +20% XP from tasks, bonus strength
    MAGE = "mage"            # +20% coins, bonus intelligence
    RANGER = "ranger"        # +20% XP from habits, bonus agility
    PALADIN = "paladin"      # +10% all XP, balanced stats
    ASSASSIN = "assassin"    # +30% streak bonuses, bonus speed


class StatsDistribution(BaseModel):
    """Character stat point distribution."""
    
    strength: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Physical power - affects task XP",
        examples=[15]
    )
    intelligence: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Mental acuity - affects coin rewards",
        examples=[12]
    )
    agility: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Speed and reflexes - affects habit XP",
        examples=[18]
    )
    vitality: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Health and endurance - affects HP",
        examples=[14]
    )
    luck: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Fortune - affects critical rewards",
        examples=[11]
    )
    
    @property
    def total(self) -> int:
        """Calculate total stat points."""
        return self.strength + self.intelligence + self.agility + self.vitality + self.luck


class CharacterCreate(BaseModel):
    """Schema for creating a new character."""
    
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Character name",
        examples=["Shadowbane"]
    )
    character_class: ClassEnum = Field(
        ...,
        description="Character class",
        examples=["warrior", "mage"]
    )
    stats: StatsDistribution = Field(
        default_factory=StatsDistribution,
        description="Initial stat distribution"
    )
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate character name."""
        if not v.replace(" ", "").replace("-", "").replace("'", "").isalnum():
            raise ValueError("Character name can only contain letters, numbers, spaces, hyphens, and apostrophes")
        return v.strip()
    
    @model_validator(mode="after")
    def validate_starting_stats(self) -> "CharacterCreate":
        """Validate starting stat total."""
        if self.stats.total > 60:  # Base 50 + 10 bonus points
            raise ValueError(f"Starting stats cannot exceed 60 points (got {self.stats.total})")
        return self


class CharacterUpdate(BaseModel):
    """Schema for updating character details."""
    
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=30,
        description="Updated character name"
    )
    avatar_id: str | None = Field(
        default=None,
        max_length=50,
        description="Selected avatar ID"
    )
    title: str | None = Field(
        default=None,
        max_length=50,
        description="Character title/epithet",
        examples=["The Unstoppable", "Habit Master"]
    )


class StatPointAllocation(BaseModel):
    """Schema for allocating stat points on level up."""
    
    strength: int = Field(
        default=0,
        ge=0,
        le=5,
        description="Points to add to strength"
    )
    intelligence: int = Field(
        default=0,
        ge=0,
        le=5,
        description="Points to add to intelligence"
    )
    agility: int = Field(
        default=0,
        ge=0,
        le=5,
        description="Points to add to agility"
    )
    vitality: int = Field(
        default=0,
        ge=0,
        le=5,
        description="Points to add to vitality"
    )
    luck: int = Field(
        default=0,
        ge=0,
        le=5,
        description="Points to add to luck"
    )
    
    @property
    def total(self) -> int:
        """Calculate total points being allocated."""
        return self.strength + self.intelligence + self.agility + self.vitality + self.luck


class EquippedItems(BaseModel):
    """Currently equipped items."""
    
    weapon_id: UUID | None = Field(
        default=None,
        description="Equipped weapon"
    )
    armor_id: UUID | None = Field(
        default=None,
        description="Equipped armor"
    )
    accessory_id: UUID | None = Field(
        default=None,
        description="Equipped accessory"
    )
    pet_id: UUID | None = Field(
        default=None,
        description="Active pet companion"
    )


class CharacterResponse(BaseModel):
    """Schema for character response with full details."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="Unique character identifier",
        examples=["550e8400-e29b-41d4-a716-446655440004"]
    )
    user_id: UUID = Field(
        ...,
        description="Owner's user ID"
    )
    name: str = Field(
        ...,
        description="Character name",
        examples=["Shadowbane"]
    )
    character_class: ClassEnum = Field(
        ...,
        description="Character class"
    )
    title: str | None = Field(
        default=None,
        description="Character title",
        examples=["The Unstoppable"]
    )
    avatar_id: str = Field(
        default="default",
        description="Selected avatar"
    )
    level: int = Field(
        default=1,
        ge=1,
        le=100,
        description="Character level",
        examples=[15]
    )
    current_xp: int = Field(
        default=0,
        ge=0,
        description="XP in current level",
        examples=[450]
    )
    xp_to_next_level: int = Field(
        default=100,
        ge=1,
        description="XP needed for next level",
        examples=[1000]
    )
    total_xp: int = Field(
        default=0,
        ge=0,
        description="Total XP earned lifetime",
        examples=[15450]
    )
    hp: int = Field(
        default=100,
        ge=0,
        description="Current health points",
        examples=[85]
    )
    max_hp: int = Field(
        default=100,
        ge=1,
        description="Maximum health points",
        examples=[100]
    )
    stats: StatsDistribution = Field(
        ...,
        description="Current stat distribution"
    )
    unallocated_points: int = Field(
        default=0,
        ge=0,
        description="Available stat points to allocate",
        examples=[3]
    )
    equipped: EquippedItems = Field(
        default_factory=EquippedItems,
        description="Currently equipped items"
    )
    coins: int = Field(
        default=0,
        ge=0,
        description="Current coin balance",
        examples=[1250]
    )
    gems: int = Field(
        default=0,
        ge=0,
        description="Premium currency balance",
        examples=[50]
    )
    created_at: datetime = Field(
        ...,
        description="When the character was created"
    )
    updated_at: datetime = Field(
        ...,
        description="When the character was last updated"
    )


class CharacterSummary(BaseModel):
    """Lightweight character summary for listings."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    character_class: ClassEnum
    level: int
    avatar_id: str
    title: str | None = None


class LevelUpResult(BaseModel):
    """Result of leveling up."""
    
    new_level: int = Field(
        ...,
        description="New character level"
    )
    stat_points_gained: int = Field(
        default=3,
        description="Stat points earned"
    )
    hp_increase: int = Field(
        default=10,
        description="Max HP increase"
    )
    rewards: list[str] = Field(
        default_factory=list,
        description="Special rewards unlocked",
        examples=[["New avatar: Dragon Knight", "Class skill: Berserker Rage"]]
    )
