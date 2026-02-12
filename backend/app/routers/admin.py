"""
Admin routes for managing items, classes, and appearances.
"""
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.item import Item
from app.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

# ==================== SCHEMAS ====================

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    rarity: str = "common"
    price: int = 100
    strength_bonus: int = 0
    endurance_bonus: int = 0
    agility_bonus: int = 0
    intelligence_bonus: int = 0
    charisma_bonus: int = 0
    sprite_url: Optional[str] = None
    is_available: bool = True
    required_level: int = 1

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    rarity: Optional[str] = None
    price: Optional[int] = None
    strength_bonus: Optional[int] = None
    endurance_bonus: Optional[int] = None
    agility_bonus: Optional[int] = None
    intelligence_bonus: Optional[int] = None
    charisma_bonus: Optional[int] = None
    sprite_url: Optional[str] = None
    is_available: Optional[bool] = None
    required_level: Optional[int] = None

class ItemResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    category: str
    rarity: str
    price: int
    strength_bonus: int
    endurance_bonus: int
    agility_bonus: int
    intelligence_bonus: int
    charisma_bonus: int
    sprite_url: Optional[str]
    is_available: bool
    required_level: int

    class Config:
        from_attributes = True

# ==================== ITEMS CRUD ====================

@router.get("/items", response_model=List[ItemResponse])
async def list_all_items(db: AsyncSession = Depends(get_db)):
    """List all items (admin view)."""
    result = await db.execute(select(Item).order_by(Item.category, Item.rarity, Item.name))
    items = result.scalars().all()
    return items

@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new item."""
    item = Item(
        id=uuid4(),
        name=item_data.name,
        description=item_data.description,
        category=item_data.category,
        rarity=item_data.rarity,
        price=item_data.price,
        strength_bonus=item_data.strength_bonus,
        endurance_bonus=item_data.endurance_bonus,
        agility_bonus=item_data.agility_bonus,
        intelligence_bonus=item_data.intelligence_bonus,
        charisma_bonus=item_data.charisma_bonus,
        sprite_url=item_data.sprite_url,
        is_available=item_data.is_available,
        is_limited=False,
        required_level=item_data.required_level,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing item."""
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete an item."""
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await db.delete(item)
    await db.commit()

# ==================== BULK OPERATIONS ====================

@router.post("/items/bulk", response_model=dict)
async def bulk_create_items(
    items: List[ItemCreate],
    db: AsyncSession = Depends(get_db),
):
    """Create multiple items at once."""
    created = 0
    for item_data in items:
        item = Item(
            id=uuid4(),
            name=item_data.name,
            description=item_data.description,
            category=item_data.category,
            rarity=item_data.rarity,
            price=item_data.price,
            strength_bonus=item_data.strength_bonus,
            endurance_bonus=item_data.endurance_bonus,
            agility_bonus=item_data.agility_bonus,
            intelligence_bonus=item_data.intelligence_bonus,
            charisma_bonus=item_data.charisma_bonus,
            sprite_url=item_data.sprite_url,
            is_available=item_data.is_available,
            is_limited=False,
            required_level=item_data.required_level,
        )
        db.add(item)
        created += 1
    
    await db.commit()
    return {"created": created}

@router.delete("/items/all", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_items(db: AsyncSession = Depends(get_db)):
    """Delete all items (dangerous!)."""
    from sqlalchemy import text
    await db.execute(text("DELETE FROM user_inventory"))
    await db.execute(delete(Item))
    await db.commit()

# ==================== STATS ====================

@router.get("/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    """Get admin statistics."""
    from sqlalchemy import func, text
    
    # Count items by category
    result = await db.execute(
        select(Item.category, func.count(Item.id))
        .group_by(Item.category)
    )
    items_by_category = {row[0]: row[1] for row in result.fetchall()}
    
    # Count items by rarity
    result = await db.execute(
        select(Item.rarity, func.count(Item.id))
        .group_by(Item.rarity)
    )
    items_by_rarity = {row[0]: row[1] for row in result.fetchall()}
    
    # Total users
    result = await db.execute(text("SELECT COUNT(*) FROM users"))
    total_users = result.scalar()
    
    # Total characters
    result = await db.execute(text("SELECT COUNT(*) FROM characters"))
    total_characters = result.scalar()
    
    return {
        "items": {
            "total": sum(items_by_category.values()),
            "by_category": items_by_category,
            "by_rarity": items_by_rarity,
        },
        "users": total_users,
        "characters": total_characters,
    }
