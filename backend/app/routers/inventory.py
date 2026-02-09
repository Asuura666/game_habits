"""
Inventory Router - User Item Management

Endpoints for viewing and managing owned items.
"""
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.deps import CurrentUserWithCharacter, DBSession
from app.models.character import Character
from app.models.inventory import UserInventory
from app.models.item import Item

logger = structlog.get_logger()

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# =============================================================================
# Response Models
# =============================================================================


class InventoryItemResponse(BaseModel):
    """Item in user's inventory."""
    
    id: UUID  # Inventory entry ID
    item_id: UUID
    name: str
    description: str | None
    category: str
    rarity: str
    strength_bonus: int
    endurance_bonus: int
    agility_bonus: int
    intelligence_bonus: int
    charisma_bonus: int
    sprite_url: str | None
    is_equipped: bool
    equipped_slot: str | None


class InventoryResponse(BaseModel):
    """Full inventory response."""
    
    items: list[InventoryItemResponse]
    total: int
    equipped_count: int
    total_stats_bonus: dict[str, int]


class EquippedItemsResponse(BaseModel):
    """Currently equipped items by slot."""
    
    weapon: InventoryItemResponse | None
    armor: InventoryItemResponse | None
    helmet: InventoryItemResponse | None
    accessory: InventoryItemResponse | None
    pet: InventoryItemResponse | None
    total_stats_bonus: dict[str, int]


class EquipResult(BaseModel):
    """Result of equipping an item."""
    
    success: bool
    message: str
    equipped_item: InventoryItemResponse
    unequipped_item: InventoryItemResponse | None = None


class UnequipResult(BaseModel):
    """Result of unequipping an item."""
    
    success: bool
    message: str
    unequipped_item: InventoryItemResponse


# =============================================================================
# Helper Functions
# =============================================================================


def inventory_entry_to_response(entry: UserInventory) -> InventoryItemResponse:
    """Convert inventory entry to response model."""
    item = entry.item
    return InventoryItemResponse(
        id=entry.id,
        item_id=item.id,
        name=item.name,
        description=item.description,
        category=item.category,
        rarity=item.rarity,
        strength_bonus=item.strength_bonus,
        endurance_bonus=item.endurance_bonus,
        agility_bonus=item.agility_bonus,
        intelligence_bonus=item.intelligence_bonus,
        charisma_bonus=item.charisma_bonus,
        sprite_url=item.sprite_url,
        is_equipped=entry.is_equipped,
        equipped_slot=entry.equipped_slot,
    )


def calculate_total_bonus(items: list[InventoryItemResponse]) -> dict[str, int]:
    """Calculate total stat bonuses from equipped items."""
    totals = {
        "strength": 0,
        "endurance": 0,
        "agility": 0,
        "intelligence": 0,
        "charisma": 0,
    }
    
    for item in items:
        if item.is_equipped:
            totals["strength"] += item.strength_bonus
            totals["endurance"] += item.endurance_bonus
            totals["agility"] += item.agility_bonus
            totals["intelligence"] += item.intelligence_bonus
            totals["charisma"] += item.charisma_bonus
    
    return totals


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/",
    response_model=InventoryResponse,
    summary="Get Inventory",
    description="Get all items in the user's inventory.",
)
async def get_inventory(
    current_user: CurrentUserWithCharacter,
    db: DBSession,
    category: str | None = Query(None, description="Filter by category"),
    equipped_only: bool = Query(False, description="Show only equipped items"),
) -> InventoryResponse:
    """Get user's inventory."""
    query = (
        select(UserInventory)
        .options(selectinload(UserInventory.item))
        .where(UserInventory.user_id == current_user.id)
    )
    
    if equipped_only:
        query = query.where(UserInventory.is_equipped == True)
    
    result = await db.execute(query)
    entries = result.scalars().all()
    
    # Filter by category in Python (item is loaded via selectinload)
    if category:
        entries = [e for e in entries if e.item.category == category]
    
    items = [inventory_entry_to_response(e) for e in entries]
    equipped_items = [i for i in items if i.is_equipped]
    
    return InventoryResponse(
        items=items,
        total=len(items),
        equipped_count=len(equipped_items),
        total_stats_bonus=calculate_total_bonus(items),
    )


@router.post(
    "/equip/{inventory_id}",
    response_model=EquipResult,
    summary="Equip Item",
    description="Equip an item from inventory. Automatically unequips any item in the same slot.",
)
async def equip_item(
    inventory_id: UUID,
    current_user: CurrentUserWithCharacter,
    db: DBSession,
) -> EquipResult:
    """Equip an item from inventory."""
    character = current_user.character
    
    # Get inventory entry
    result = await db.execute(
        select(UserInventory)
        .options(selectinload(UserInventory.item))
        .where(
            UserInventory.id == inventory_id,
            UserInventory.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in your inventory",
        )
    
    if entry.is_equipped:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item is already equipped",
        )
    
    item = entry.item
    slot = item.category  # weapon, armor, helmet, accessory, pet
    
    # Map slot to character field
    slot_field_map = {
        "weapon": "equipped_weapon_id",
        "armor": "equipped_armor_id",
        "helmet": "equipped_helmet_id",
        "accessory": "equipped_accessory_id",
        "pet": "equipped_pet_id",
    }
    
    if slot not in slot_field_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot equip items of category: {slot}",
        )
    
    # Check for currently equipped item in same slot
    unequipped_response = None
    current_equipped_id = getattr(character, slot_field_map[slot])
    
    if current_equipped_id:
        # Unequip current item
        current_result = await db.execute(
            select(UserInventory)
            .options(selectinload(UserInventory.item))
            .where(
                UserInventory.user_id == current_user.id,
                UserInventory.item_id == current_equipped_id,
                UserInventory.is_equipped == True,
            )
        )
        current_entry = current_result.scalar_one_or_none()
        
        if current_entry:
            current_entry.unequip()
            unequipped_response = inventory_entry_to_response(current_entry)
    
    # Equip new item
    entry.equip(slot)
    setattr(character, slot_field_map[slot], item.id)
    
    await db.flush()
    
    logger.info(
        "Item equipped",
        user_id=str(current_user.id),
        item_id=str(item.id),
        slot=slot,
    )
    
    return EquipResult(
        success=True,
        message=f"Equipped {item.name}",
        equipped_item=inventory_entry_to_response(entry),
        unequipped_item=unequipped_response,
    )


@router.post(
    "/unequip/{slot}",
    response_model=UnequipResult,
    summary="Unequip Item",
    description="Unequip the item from a specific slot.",
)
async def unequip_item(
    slot: str,
    current_user: CurrentUserWithCharacter,
    db: DBSession,
) -> UnequipResult:
    """Unequip item from a slot."""
    character = current_user.character
    
    # Validate slot
    valid_slots = ["weapon", "armor", "helmet", "accessory", "pet"]
    if slot not in valid_slots:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid slot. Must be one of: {', '.join(valid_slots)}",
        )
    
    slot_field_map = {
        "weapon": "equipped_weapon_id",
        "armor": "equipped_armor_id",
        "helmet": "equipped_helmet_id",
        "accessory": "equipped_accessory_id",
        "pet": "equipped_pet_id",
    }
    
    equipped_id = getattr(character, slot_field_map[slot])
    
    if not equipped_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No item equipped in {slot} slot",
        )
    
    # Find inventory entry
    result = await db.execute(
        select(UserInventory)
        .options(selectinload(UserInventory.item))
        .where(
            UserInventory.user_id == current_user.id,
            UserInventory.item_id == equipped_id,
            UserInventory.is_equipped == True,
        )
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Equipped item not found in inventory",
        )
    
    # Unequip
    entry.unequip()
    setattr(character, slot_field_map[slot], None)
    
    await db.flush()
    
    logger.info(
        "Item unequipped",
        user_id=str(current_user.id),
        item_id=str(entry.item_id),
        slot=slot,
    )
    
    return UnequipResult(
        success=True,
        message=f"Unequipped {entry.item.name}",
        unequipped_item=inventory_entry_to_response(entry),
    )


@router.get(
    "/equipped",
    response_model=EquippedItemsResponse,
    summary="Get Equipped Items",
    description="Get all currently equipped items by slot.",
)
async def get_equipped_items(
    current_user: CurrentUserWithCharacter,
    db: DBSession,
) -> EquippedItemsResponse:
    """Get currently equipped items."""
    character = current_user.character
    
    # Get all equipped inventory entries
    result = await db.execute(
        select(UserInventory)
        .options(selectinload(UserInventory.item))
        .where(
            UserInventory.user_id == current_user.id,
            UserInventory.is_equipped == True,
        )
    )
    entries = result.scalars().all()
    
    # Organize by slot
    equipped = {
        "weapon": None,
        "armor": None,
        "helmet": None,
        "accessory": None,
        "pet": None,
    }
    
    items = []
    for entry in entries:
        response = inventory_entry_to_response(entry)
        items.append(response)
        if entry.equipped_slot in equipped:
            equipped[entry.equipped_slot] = response
    
    return EquippedItemsResponse(
        weapon=equipped["weapon"],
        armor=equipped["armor"],
        helmet=equipped["helmet"],
        accessory=equipped["accessory"],
        pet=equipped["pet"],
        total_stats_bonus=calculate_total_bonus(items),
    )
