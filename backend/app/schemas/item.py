"""Item schemas for the in-game shop and inventory."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ItemCategory(str, Enum):
    """Categories of items available in the shop."""
    
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    PET = "pet"
    COSMETIC = "cosmetic"
    BOOST = "boost"


class Rarity(str, Enum):
    """Item rarity levels with associated drop rates and power."""
    
    COMMON = "common"          # 50% drop rate, 1x stats
    UNCOMMON = "uncommon"      # 25% drop rate, 1.5x stats
    RARE = "rare"              # 15% drop rate, 2x stats
    EPIC = "epic"              # 8% drop rate, 3x stats
    LEGENDARY = "legendary"    # 2% drop rate, 5x stats


class ItemEffect(BaseModel):
    """Effect that an item provides when equipped or used."""
    
    effect_type: str = Field(
        ...,
        description="Type of effect",
        examples=["xp_boost", "coin_boost", "stat_bonus", "streak_protection"]
    )
    value: float = Field(
        ...,
        description="Effect magnitude",
        examples=[1.1, 5, 0.2]
    )
    duration_hours: int | None = Field(
        default=None,
        ge=1,
        description="Duration for temporary effects (consumables)",
        examples=[24]
    )
    stat_target: str | None = Field(
        default=None,
        description="Which stat this affects (for stat bonuses)",
        examples=["strength", "intelligence"]
    )


class ItemBase(BaseModel):
    """Base item schema."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Item name",
        examples=["Sword of Discipline"]
    )
    description: str = Field(
        ...,
        max_length=500,
        description="Item description",
        examples=["A legendary blade forged from pure willpower. Grants +10% XP from tasks."]
    )
    category: ItemCategory = Field(
        ...,
        description="Item category"
    )
    rarity: Rarity = Field(
        ...,
        description="Item rarity"
    )
    icon: str = Field(
        default="⚔️",
        max_length=10,
        description="Emoji icon",
        examples=["⚔️", "🛡️", "💍"]
    )
    image_url: str | None = Field(
        default=None,
        max_length=500,
        description="URL to item image"
    )


class ItemResponse(ItemBase):
    """Schema for item response with full details."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="Unique item identifier",
        examples=["550e8400-e29b-41d4-a716-446655440005"]
    )
    price_coins: int = Field(
        ...,
        ge=0,
        description="Price in coins",
        examples=[500]
    )
    price_gems: int = Field(
        default=0,
        ge=0,
        description="Price in premium gems",
        examples=[0]
    )
    level_required: int = Field(
        default=1,
        ge=1,
        le=100,
        description="Minimum level to purchase/equip",
        examples=[10]
    )
    class_restriction: str | None = Field(
        default=None,
        description="Class that can use this item (None = all)",
        examples=["warrior", None]
    )
    effects: list[ItemEffect] = Field(
        default_factory=list,
        description="Item effects when equipped/used"
    )
    is_tradeable: bool = Field(
        default=True,
        description="Whether the item can be traded"
    )
    is_available: bool = Field(
        default=True,
        description="Whether the item is available in shop"
    )
    max_stack: int = Field(
        default=1,
        ge=1,
        le=999,
        description="Maximum stack size (for consumables)",
        examples=[1, 99]
    )
    created_at: datetime = Field(
        ...,
        description="When the item was added"
    )


class InventoryItem(BaseModel):
    """Schema for an item in user's inventory."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="Unique inventory entry ID"
    )
    item: ItemResponse = Field(
        ...,
        description="The item details"
    )
    quantity: int = Field(
        default=1,
        ge=1,
        description="Number of this item owned",
        examples=[1, 5]
    )
    is_equipped: bool = Field(
        default=False,
        description="Whether the item is currently equipped"
    )
    acquired_at: datetime = Field(
        ...,
        description="When the item was acquired"
    )


class ShopCategory(BaseModel):
    """Category of items in the shop."""
    
    category: ItemCategory = Field(
        ...,
        description="Category type"
    )
    display_name: str = Field(
        ...,
        description="Display name for the category",
        examples=["Weapons", "Armor", "Pets"]
    )
    icon: str = Field(
        ...,
        description="Category icon",
        examples=["⚔️", "🛡️", "🐾"]
    )
    items: list[ItemResponse] = Field(
        default_factory=list,
        description="Items in this category"
    )


class PurchaseRequest(BaseModel):
    """Schema for purchasing an item."""
    
    item_id: UUID = Field(
        ...,
        description="ID of the item to purchase"
    )
    quantity: int = Field(
        default=1,
        ge=1,
        le=99,
        description="Quantity to purchase"
    )
    use_gems: bool = Field(
        default=False,
        description="Pay with gems instead of coins"
    )


class PurchaseResult(BaseModel):
    """Result of a purchase transaction."""
    
    success: bool = Field(
        ...,
        description="Whether the purchase succeeded"
    )
    item: ItemResponse = Field(
        ...,
        description="The purchased item"
    )
    quantity: int = Field(
        ...,
        description="Quantity purchased"
    )
    total_cost: int = Field(
        ...,
        description="Total cost paid"
    )
    currency_used: str = Field(
        ...,
        description="Currency type used",
        examples=["coins", "gems"]
    )
    remaining_balance: int = Field(
        ...,
        description="Remaining currency after purchase"
    )
    message: str = Field(
        ...,
        description="Purchase result message",
        examples=["Successfully purchased Sword of Discipline!"]
    )
