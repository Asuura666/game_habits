"""
Shop Router - In-Game Item Shop

Endpoints for browsing and purchasing items.
"""
from datetime import datetime, timezone
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import selectinload

from app.deps import CurrentUser, CurrentUserWithCharacter, DBSession
from app.models.inventory import UserInventory
from app.models.item import Item
from app.models.transaction import CoinTransaction
from app.schemas.item import ItemResponse, PurchaseResult, Rarity

logger = structlog.get_logger()

router = APIRouter(prefix="/shop", tags=["Shop"])


# =============================================================================
# Response Models
# =============================================================================


class ShopItemResponse(BaseModel):
    """Shop item with ownership status."""
    
    id: UUID
    name: str
    description: str | None
    category: str
    rarity: str
    price: int
    strength_bonus: int
    endurance_bonus: int
    agility_bonus: int
    intelligence_bonus: int
    charisma_bonus: int
    sprite_url: str | None
    is_available: bool
    is_limited: bool
    required_level: int
    is_owned: bool = False
    can_afford: bool = True


class ShopListResponse(BaseModel):
    """Paginated shop item list."""
    
    items: list[ShopItemResponse]
    total: int
    page: int
    per_page: int
    has_next: bool


class PurchaseHistoryEntry(BaseModel):
    """Purchase history entry."""
    
    item_id: UUID
    item_name: str
    item_category: str
    item_rarity: str
    price_paid: int
    purchased_at: datetime


class PurchaseHistoryResponse(BaseModel):
    """Purchase history list."""
    
    purchases: list[PurchaseHistoryEntry]
    total: int
    total_spent: int


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/items",
    response_model=ShopListResponse,
    summary="List Shop Items",
    description="Get all available items in the shop with filtering options.",
)
async def list_shop_items(
    current_user: CurrentUser,
    db: DBSession,
    category: str | None = Query(None, description="Filter by category (weapon, armor, etc.)"),
    rarity: str | None = Query(None, description="Filter by rarity (common, rare, etc.)"),
    max_price: int | None = Query(None, ge=0, description="Maximum price filter"),
    min_level: int | None = Query(None, ge=1, description="Minimum required level"),
    search: str | None = Query(None, min_length=2, description="Search by name"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=50, description="Items per page"),
) -> ShopListResponse:
    """Get paginated list of shop items."""
    now = datetime.now(timezone.utc)
    
    # Base query - available items
    query = select(Item).where(
        Item.is_available == True,
        or_(
            Item.available_from.is_(None),
            Item.available_from <= now,
        ),
        or_(
            Item.available_until.is_(None),
            Item.available_until >= now,
        ),
    )
    
    # Apply filters
    if category:
        query = query.where(Item.category == category)
    if rarity:
        query = query.where(Item.rarity == rarity)
    if max_price:
        query = query.where(Item.price <= max_price)
    if min_level:
        query = query.where(Item.required_level >= min_level)
    if search:
        query = query.where(Item.name.ilike(f"%{search}%"))
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    offset = (page - 1) * per_page
    query = query.order_by(Item.rarity, Item.price).offset(offset).limit(per_page)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Get user's owned items
    owned_result = await db.execute(
        select(UserInventory.item_id).where(UserInventory.user_id == current_user.id)
    )
    owned_ids = {row[0] for row in owned_result.fetchall()}
    
    # Build response
    shop_items = []
    for item in items:
        shop_items.append(
            ShopItemResponse(
                id=item.id,
                name=item.name,
                description=item.description,
                category=item.category,
                rarity=item.rarity,
                price=item.price,
                strength_bonus=item.strength_bonus,
                endurance_bonus=item.endurance_bonus,
                agility_bonus=item.agility_bonus,
                intelligence_bonus=item.intelligence_bonus,
                charisma_bonus=item.charisma_bonus,
                sprite_url=item.sprite_url,
                is_available=item.is_available,
                is_limited=item.is_limited,
                required_level=item.required_level,
                is_owned=item.id in owned_ids,
                can_afford=current_user.coins >= item.price,
            )
        )
    
    return ShopListResponse(
        items=shop_items,
        total=total,
        page=page,
        per_page=per_page,
        has_next=(offset + per_page) < total,
    )


@router.get(
    "/items/{item_id}",
    response_model=ShopItemResponse,
    summary="Get Item Details",
    description="Get detailed information about a specific shop item.",
)
async def get_item_details(
    item_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> ShopItemResponse:
    """Get details of a specific item."""
    result = await db.execute(
        select(Item).where(Item.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    # Check if owned
    owned_result = await db.execute(
        select(UserInventory).where(
            UserInventory.user_id == current_user.id,
            UserInventory.item_id == item_id,
        )
    )
    is_owned = owned_result.scalar_one_or_none() is not None
    
    return ShopItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        category=item.category,
        rarity=item.rarity,
        price=item.price,
        strength_bonus=item.strength_bonus,
        endurance_bonus=item.endurance_bonus,
        agility_bonus=item.agility_bonus,
        intelligence_bonus=item.intelligence_bonus,
        charisma_bonus=item.charisma_bonus,
        sprite_url=item.sprite_url,
        is_available=item.is_available,
        is_limited=item.is_limited,
        required_level=item.required_level,
        is_owned=is_owned,
        can_afford=current_user.coins >= item.price,
    )


@router.post(
    "/buy/{item_id}",
    response_model=PurchaseResult,
    summary="Purchase Item",
    description="Purchase an item from the shop using coins.",
)
async def buy_item(
    item_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> PurchaseResult:
    """Purchase an item from the shop."""
    now = datetime.now(timezone.utc)
    
    # Get item
    result = await db.execute(
        select(Item).where(Item.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    # Check availability
    if not item.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item is not available for purchase",
        )
    
    if item.available_from and item.available_from > now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item is not yet available",
        )
    
    if item.available_until and item.available_until < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item is no longer available",
        )
    
    # Check level requirement
    if current_user.level < item.required_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You need to be level {item.required_level} to purchase this item",
        )
    
    # Check if already owned
    owned_result = await db.execute(
        select(UserInventory).where(
            UserInventory.user_id == current_user.id,
            UserInventory.item_id == item_id,
        )
    )
    if owned_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already own this item",
        )
    
    # Check sufficient funds
    if current_user.coins < item.price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough coins. You have {current_user.coins}, need {item.price}",
        )
    
    # Process purchase
    current_user.coins -= item.price
    
    # Add to inventory
    inventory_entry = UserInventory(
        user_id=current_user.id,
        item_id=item.id,
        is_equipped=False,
    )
    db.add(inventory_entry)
    
    # Create transaction record
    transaction = CoinTransaction(
        user_id=current_user.id,
        amount=-item.price,
        transaction_type="purchase",
        reference_id=item.id,
        description=f"Purchased {item.name}",
        balance_after=current_user.coins,
    )
    db.add(transaction)
    
    await db.flush()
    
    logger.info(
        "Item purchased",
        user_id=str(current_user.id),
        item_id=str(item.id),
        item_name=item.name,
        price=item.price,
    )
    
    return PurchaseResult(
        success=True,
        item=ItemResponse(
            id=item.id,
            name=item.name,
            description=item.description or "",
            category=item.category,
            rarity=item.rarity,
            icon="🎁",
            price_coins=item.price,
            effects=[],
            created_at=item.created_at,
        ),
        quantity=1,
        total_cost=item.price,
        currency_used="coins",
        remaining_balance=current_user.coins,
        message=f"Successfully purchased {item.name}!",
    )


@router.get(
    "/featured",
    response_model=list[ShopItemResponse],
    summary="Featured Items",
    description="Get featured/recommended items in the shop.",
)
async def get_featured_items(
    current_user: CurrentUser,
    db: DBSession,
) -> list[ShopItemResponse]:
    """Get featured items (limited, rare, or new items)."""
    now = datetime.now(timezone.utc)
    
    # Get limited time items first, then rare/epic/legendary items
    result = await db.execute(
        select(Item)
        .where(
            Item.is_available == True,
            or_(
                Item.is_limited == True,
                Item.rarity.in_(["rare", "epic", "legendary"]),
            ),
        )
        .order_by(
            Item.is_limited.desc(),
            Item.rarity,
            Item.created_at.desc(),
        )
        .limit(8)
    )
    items = result.scalars().all()
    
    # Get user's owned items
    owned_result = await db.execute(
        select(UserInventory.item_id).where(UserInventory.user_id == current_user.id)
    )
    owned_ids = {row[0] for row in owned_result.fetchall()}
    
    featured = []
    for item in items:
        featured.append(
            ShopItemResponse(
                id=item.id,
                name=item.name,
                description=item.description,
                category=item.category,
                rarity=item.rarity,
                price=item.price,
                strength_bonus=item.strength_bonus,
                endurance_bonus=item.endurance_bonus,
                agility_bonus=item.agility_bonus,
                intelligence_bonus=item.intelligence_bonus,
                charisma_bonus=item.charisma_bonus,
                sprite_url=item.sprite_url,
                is_available=item.is_available,
                is_limited=item.is_limited,
                required_level=item.required_level,
                is_owned=item.id in owned_ids,
                can_afford=current_user.coins >= item.price,
            )
        )
    
    return featured


@router.get(
    "/history",
    response_model=PurchaseHistoryResponse,
    summary="Purchase History",
    description="Get the user's purchase history.",
)
async def get_purchase_history(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
) -> PurchaseHistoryResponse:
    """Get user's purchase history."""
    # Get purchase transactions
    result = await db.execute(
        select(CoinTransaction)
        .where(
            CoinTransaction.user_id == current_user.id,
            CoinTransaction.transaction_type == "purchase",
        )
        .order_by(CoinTransaction.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    transactions = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count()).where(
            CoinTransaction.user_id == current_user.id,
            CoinTransaction.transaction_type == "purchase",
        )
    )
    total = count_result.scalar() or 0
    
    # Get total spent
    spent_result = await db.execute(
        select(func.sum(func.abs(CoinTransaction.amount))).where(
            CoinTransaction.user_id == current_user.id,
            CoinTransaction.transaction_type == "purchase",
        )
    )
    total_spent = spent_result.scalar() or 0
    
    # Get item details
    item_ids = [t.reference_id for t in transactions if t.reference_id]
    items_map = {}
    if item_ids:
        items_result = await db.execute(
            select(Item).where(Item.id.in_(item_ids))
        )
        items_map = {item.id: item for item in items_result.scalars().all()}
    
    purchases = []
    for tx in transactions:
        if tx.reference_id and tx.reference_id in items_map:
            item = items_map[tx.reference_id]
            purchases.append(
                PurchaseHistoryEntry(
                    item_id=item.id,
                    item_name=item.name,
                    item_category=item.category,
                    item_rarity=item.rarity,
                    price_paid=abs(tx.amount),
                    purchased_at=tx.created_at,
                )
            )
    
    return PurchaseHistoryResponse(
        purchases=purchases,
        total=total,
        total_spent=total_spent,
    )
