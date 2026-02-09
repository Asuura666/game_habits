"""
Characters Router - RPG Character Management

Endpoints for creating, viewing, and customizing player characters.
"""
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.deps import CurrentUser, CurrentUserWithCharacter, DBSession
from app.models.character import Character
from app.models.inventory import UserInventory
from app.models.item import Item
from app.schemas.character import (
    CharacterCreate,
    CharacterResponse,
    CharacterUpdate,
    EquippedItems,
    StatPointAllocation,
    StatsDistribution,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/characters", tags=["Characters"])


# =============================================================================
# Response Models
# =============================================================================


def character_to_response(character: Character, user) -> CharacterResponse:
    """Convert Character model to CharacterResponse."""
    return CharacterResponse(
        id=character.id,
        user_id=character.user_id,
        name=character.name,
        character_class=character.character_class,
        title=None,  # TODO: Add title field to model
        avatar_id="default",
        level=user.level,
        current_xp=user.total_xp % 1000,  # Simplified XP calculation
        xp_to_next_level=1000,
        total_xp=user.total_xp,
        hp=100,  # TODO: Track current HP
        max_hp=100 + (character.endurance * 5),
        stats=StatsDistribution(
            strength=character.strength,
            intelligence=character.intelligence,
            agility=character.agility,
            vitality=character.endurance,
            luck=character.charisma,
        ),
        unallocated_points=character.unallocated_points,
        equipped=EquippedItems(
            weapon_id=character.equipped_weapon_id,
            armor_id=character.equipped_armor_id,
            accessory_id=character.equipped_accessory_id,
            pet_id=character.equipped_pet_id,
        ),
        coins=user.coins,
        gems=0,
        created_at=character.created_at,
        updated_at=character.updated_at,
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/me",
    response_model=CharacterResponse,
    summary="Get My Character",
    description="Get the current user's character with full stats and equipment.",
)
async def get_my_character(
    current_user: CurrentUserWithCharacter,
) -> CharacterResponse:
    """Get the authenticated user's character."""
    return character_to_response(current_user.character, current_user)


@router.post(
    "/",
    response_model=CharacterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Character",
    description="Create a new character during onboarding. Users can only have one character.",
)
async def create_character(
    data: CharacterCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> CharacterResponse:
    """Create a new character for the current user."""
    # Check if user already has a character
    if current_user.character:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a character. Delete it first to create a new one.",
        )
    
    # Create character
    character = Character(
        user_id=current_user.id,
        name=data.name,
        character_class=data.character_class.value,
        gender="neutral",
        skin_color="light",
        hair_style="short",
        hair_color="brown",
        eye_color="blue",
        strength=data.stats.strength,
        endurance=data.stats.vitality,
        agility=data.stats.agility,
        intelligence=data.stats.intelligence,
        charisma=data.stats.luck,
        unallocated_points=0,
    )
    
    db.add(character)
    await db.flush()
    await db.refresh(character)
    
    logger.info(
        "Character created",
        user_id=str(current_user.id),
        character_id=str(character.id),
        character_class=character.character_class,
    )
    
    return character_to_response(character, current_user)


@router.put(
    "/me",
    response_model=CharacterResponse,
    summary="Update Character Appearance",
    description="Update character name, avatar, or title.",
)
async def update_character(
    data: CharacterUpdate,
    current_user: CurrentUserWithCharacter,
    db: DBSession,
) -> CharacterResponse:
    """Update the current user's character."""
    character = current_user.character
    
    if data.name is not None:
        character.name = data.name
    
    # TODO: Add avatar_id and title fields to model
    # if data.avatar_id is not None:
    #     character.avatar_id = data.avatar_id
    # if data.title is not None:
    #     character.title = data.title
    
    await db.flush()
    await db.refresh(character)
    
    logger.info(
        "Character updated",
        user_id=str(current_user.id),
        character_id=str(character.id),
    )
    
    return character_to_response(character, current_user)


@router.post(
    "/stats",
    response_model=CharacterResponse,
    summary="Distribute Stat Points",
    description="Allocate unspent stat points to character attributes.",
)
async def distribute_stats(
    data: StatPointAllocation,
    current_user: CurrentUserWithCharacter,
    db: DBSession,
) -> CharacterResponse:
    """Distribute unallocated stat points."""
    character = current_user.character
    points_to_allocate = data.total
    
    # Validate sufficient points
    if points_to_allocate > character.unallocated_points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough unallocated points. You have {character.unallocated_points}, trying to spend {points_to_allocate}.",
        )
    
    if points_to_allocate == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No points to allocate.",
        )
    
    # Apply stat points
    character.strength += data.strength
    character.intelligence += data.intelligence
    character.agility += data.agility
    character.endurance += data.vitality
    character.charisma += data.luck
    character.unallocated_points -= points_to_allocate
    
    await db.flush()
    await db.refresh(character)
    
    logger.info(
        "Stats distributed",
        user_id=str(current_user.id),
        character_id=str(character.id),
        points_spent=points_to_allocate,
    )
    
    return character_to_response(character, current_user)


@router.get(
    "/preview",
    summary="Preview Equipment",
    description="Preview how the character would look with specific equipment.",
)
async def preview_equipment(
    weapon_id: UUID | None = None,
    armor_id: UUID | None = None,
    helmet_id: UUID | None = None,
    accessory_id: UUID | None = None,
    pet_id: UUID | None = None,
    current_user: CurrentUserWithCharacter = None,
    db: DBSession = None,
) -> dict:
    """
    Preview character appearance with different equipment.
    
    Returns the character sprite composition with the specified items.
    """
    character = current_user.character
    
    # Collect item IDs to fetch
    item_ids = [
        item_id for item_id in [weapon_id, armor_id, helmet_id, accessory_id, pet_id]
        if item_id is not None
    ]
    
    items_data = {}
    if item_ids:
        # Fetch items
        result = await db.execute(
            select(Item).where(Item.id.in_(item_ids))
        )
        items = result.scalars().all()
        
        for item in items:
            items_data[str(item.id)] = {
                "id": str(item.id),
                "name": item.name,
                "category": item.category,
                "sprite_url": item.sprite_url,
                "sprite_layer": item.sprite_layer,
            }
    
    # Build preview response
    preview = {
        "character": {
            "name": character.name,
            "class": character.character_class,
            "gender": character.gender,
            "skin_color": character.skin_color,
            "hair_style": character.hair_style,
            "hair_color": character.hair_color,
            "eye_color": character.eye_color,
        },
        "equipment": {
            "weapon": items_data.get(str(weapon_id)) if weapon_id else None,
            "armor": items_data.get(str(armor_id)) if armor_id else None,
            "helmet": items_data.get(str(helmet_id)) if helmet_id else None,
            "accessory": items_data.get(str(accessory_id)) if accessory_id else None,
            "pet": items_data.get(str(pet_id)) if pet_id else None,
        },
        "sprite_layers": [],  # TODO: Generate sprite layer composition
    }
    
    # Build sprite layer order
    layers = []
    for slot in ["armor", "helmet", "weapon", "accessory", "pet"]:
        if preview["equipment"][slot]:
            layers.append({
                "slot": slot,
                "sprite_url": preview["equipment"][slot]["sprite_url"],
                "layer": preview["equipment"][slot]["sprite_layer"],
            })
    
    preview["sprite_layers"] = sorted(layers, key=lambda x: x["layer"])
    
    return preview
