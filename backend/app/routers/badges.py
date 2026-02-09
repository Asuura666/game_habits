"""
Badges Router - Achievement System

Endpoints for viewing and managing badges.
"""
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.deps import CurrentUser, DBSession
from app.models.badge import Badge, UserBadge

logger = structlog.get_logger()

router = APIRouter(prefix="/badges", tags=["Badges"])


# =============================================================================
# Response Models
# =============================================================================


class BadgeResponse(BaseModel):
    """Badge definition."""
    
    id: UUID
    code: str
    name: str
    description: str
    icon: str
    rarity: str
    xp_reward: int
    condition_type: str
    condition_value: dict
    is_secret: bool
    is_seasonal: bool


class UserBadgeResponse(BaseModel):
    """User's badge with unlock status."""
    
    badge: BadgeResponse
    is_unlocked: bool
    unlocked_at: str | None
    is_displayed: bool
    display_position: int | None


class BadgeDetailResponse(BaseModel):
    """Detailed badge info with stats."""
    
    badge: BadgeResponse
    is_unlocked: bool
    unlocked_at: str | None
    total_unlocks: int
    unlock_percentage: float
    is_displayed: bool


class BadgeCollectionResponse(BaseModel):
    """User's badge collection summary."""
    
    total_badges: int
    unlocked_count: int
    locked_count: int
    displayed_badges: list[UserBadgeResponse]
    recent_unlocks: list[UserBadgeResponse]
    rarest_badge: UserBadgeResponse | None


class DisplayBadgesRequest(BaseModel):
    """Request to update displayed badges."""
    
    badge_ids: list[UUID] = Field(
        ...,
        min_length=0,
        max_length=3,
        description="Up to 3 badge IDs to display on profile",
    )


class DisplayBadgesResponse(BaseModel):
    """Response after updating displayed badges."""
    
    success: bool
    displayed_badges: list[UserBadgeResponse]
    message: str


# =============================================================================
# Helper Functions
# =============================================================================


def badge_to_response(badge: Badge) -> BadgeResponse:
    """Convert Badge model to response."""
    return BadgeResponse(
        id=badge.id,
        code=badge.code,
        name=badge.name,
        description=badge.description,
        icon=badge.icon,
        rarity=badge.rarity,
        xp_reward=badge.xp_reward,
        condition_type=badge.condition_type,
        condition_value=badge.condition_value,
        is_secret=badge.is_secret,
        is_seasonal=badge.is_seasonal,
    )


def user_badge_to_response(
    badge: Badge,
    user_badge: UserBadge | None = None,
) -> UserBadgeResponse:
    """Convert Badge and optional UserBadge to response."""
    return UserBadgeResponse(
        badge=badge_to_response(badge),
        is_unlocked=user_badge is not None,
        unlocked_at=user_badge.unlocked_at.isoformat() if user_badge else None,
        is_displayed=user_badge.is_displayed if user_badge else False,
        display_position=user_badge.display_position if user_badge else None,
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/",
    response_model=list[UserBadgeResponse],
    summary="Get All Badges",
    description="Get all badges with locked/unlocked status for current user.",
)
async def get_all_badges(
    current_user: CurrentUser,
    db: DBSession,
    category: str | None = Query(None, description="Filter by condition type"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    unlocked_only: bool = Query(False, description="Show only unlocked badges"),
    include_secret: bool = Query(False, description="Include secret badges"),
) -> list[UserBadgeResponse]:
    """Get all badges with user's unlock status."""
    # Get all badges
    badge_query = select(Badge)
    
    if category:
        badge_query = badge_query.where(Badge.condition_type == category)
    if rarity:
        badge_query = badge_query.where(Badge.rarity == rarity)
    if not include_secret:
        badge_query = badge_query.where(Badge.is_secret == False)
    
    badge_query = badge_query.order_by(Badge.rarity, Badge.name)
    
    result = await db.execute(badge_query)
    badges = result.scalars().all()
    
    # Get user's unlocked badges
    user_badges_result = await db.execute(
        select(UserBadge).where(UserBadge.user_id == current_user.id)
    )
    user_badges = {ub.badge_id: ub for ub in user_badges_result.scalars().all()}
    
    response = []
    for badge in badges:
        user_badge = user_badges.get(badge.id)
        
        # Skip locked if unlocked_only
        if unlocked_only and not user_badge:
            continue
        
        # For secret badges, only show if unlocked
        if badge.is_secret and not user_badge:
            continue
        
        response.append(user_badge_to_response(badge, user_badge))
    
    return response


@router.get(
    "/unlocked",
    response_model=list[UserBadgeResponse],
    summary="Get Unlocked Badges",
    description="Get only the badges the user has unlocked.",
)
async def get_unlocked_badges(
    current_user: CurrentUser,
    db: DBSession,
) -> list[UserBadgeResponse]:
    """Get user's unlocked badges."""
    result = await db.execute(
        select(UserBadge)
        .options(selectinload(UserBadge.badge))
        .where(UserBadge.user_id == current_user.id)
        .order_by(UserBadge.unlocked_at.desc())
    )
    user_badges = result.scalars().all()
    
    return [
        user_badge_to_response(ub.badge, ub)
        for ub in user_badges
    ]


@router.get(
    "/collection",
    response_model=BadgeCollectionResponse,
    summary="Get Badge Collection Summary",
    description="Get summary of user's badge collection.",
)
async def get_badge_collection(
    current_user: CurrentUser,
    db: DBSession,
) -> BadgeCollectionResponse:
    """Get badge collection summary."""
    # Count total badges (excluding secret)
    total_result = await db.execute(
        select(func.count()).where(Badge.is_secret == False)
    )
    total_badges = total_result.scalar() or 0
    
    # Get user's badges
    user_badges_result = await db.execute(
        select(UserBadge)
        .options(selectinload(UserBadge.badge))
        .where(UserBadge.user_id == current_user.id)
        .order_by(UserBadge.unlocked_at.desc())
    )
    user_badges = user_badges_result.scalars().all()
    
    unlocked_count = len(user_badges)
    locked_count = total_badges - unlocked_count
    
    # Get displayed badges
    displayed = [
        user_badge_to_response(ub.badge, ub)
        for ub in user_badges
        if ub.is_displayed
    ]
    displayed.sort(key=lambda x: x.display_position or 99)
    
    # Recent unlocks (last 5)
    recent = [
        user_badge_to_response(ub.badge, ub)
        for ub in user_badges[:5]
    ]
    
    # Find rarest badge (by rarity tier)
    rarity_order = ["legendary", "epic", "rare", "uncommon", "common"]
    rarest = None
    for rarity in rarity_order:
        for ub in user_badges:
            if ub.badge.rarity == rarity:
                rarest = user_badge_to_response(ub.badge, ub)
                break
        if rarest:
            break
    
    return BadgeCollectionResponse(
        total_badges=total_badges,
        unlocked_count=unlocked_count,
        locked_count=locked_count,
        displayed_badges=displayed,
        recent_unlocks=recent,
        rarest_badge=rarest,
    )


@router.get(
    "/{badge_id}",
    response_model=BadgeDetailResponse,
    summary="Get Badge Details",
    description="Get detailed information about a specific badge.",
)
async def get_badge_details(
    badge_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> BadgeDetailResponse:
    """Get details of a specific badge."""
    # Get badge
    result = await db.execute(
        select(Badge).where(Badge.id == badge_id)
    )
    badge = result.scalar_one_or_none()
    
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found",
        )
    
    # Check if user has unlocked it
    user_badge_result = await db.execute(
        select(UserBadge).where(
            UserBadge.user_id == current_user.id,
            UserBadge.badge_id == badge_id,
        )
    )
    user_badge = user_badge_result.scalar_one_or_none()
    
    # If it's secret and not unlocked, hide it
    if badge.is_secret and not user_badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found",
        )
    
    # Count total unlocks
    unlock_count_result = await db.execute(
        select(func.count()).where(UserBadge.badge_id == badge_id)
    )
    total_unlocks = unlock_count_result.scalar() or 0
    
    # Calculate percentage (approximate based on total users)
    # TODO: Get actual user count
    total_users = 100  # Placeholder
    unlock_percentage = (total_unlocks / total_users * 100) if total_users > 0 else 0
    
    return BadgeDetailResponse(
        badge=badge_to_response(badge),
        is_unlocked=user_badge is not None,
        unlocked_at=user_badge.unlocked_at.isoformat() if user_badge else None,
        total_unlocks=total_unlocks,
        unlock_percentage=round(unlock_percentage, 1),
        is_displayed=user_badge.is_displayed if user_badge else False,
    )


@router.post(
    "/display",
    response_model=DisplayBadgesResponse,
    summary="Set Display Badges",
    description="Choose up to 3 badges to display on your profile.",
)
async def set_display_badges(
    data: DisplayBadgesRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> DisplayBadgesResponse:
    """Set which badges to display on profile."""
    # Validate badge count
    if len(data.badge_ids) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 badges can be displayed",
        )
    
    # Get user's badges
    result = await db.execute(
        select(UserBadge)
        .options(selectinload(UserBadge.badge))
        .where(UserBadge.user_id == current_user.id)
    )
    user_badges = {ub.badge_id: ub for ub in result.scalars().all()}
    
    # Validate all badge_ids are unlocked
    for badge_id in data.badge_ids:
        if badge_id not in user_badges:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Badge {badge_id} not unlocked",
            )
    
    # Clear current display settings
    for ub in user_badges.values():
        ub.is_displayed = False
        ub.display_position = None
    
    # Set new display badges
    displayed = []
    for position, badge_id in enumerate(data.badge_ids, start=1):
        ub = user_badges[badge_id]
        ub.is_displayed = True
        ub.display_position = position
        displayed.append(user_badge_to_response(ub.badge, ub))
    
    await db.flush()
    
    logger.info(
        "Display badges updated",
        user_id=str(current_user.id),
        badge_count=len(data.badge_ids),
    )
    
    return DisplayBadgesResponse(
        success=True,
        displayed_badges=displayed,
        message=f"Now displaying {len(displayed)} badge(s) on your profile",
    )
