"""
Streak freeze router for HabitQuest.
Allows users to freeze their streak to protect it for 24h.
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import CurrentUser
from app.models.user import User

router = APIRouter(prefix="/streak", tags=["Streak"])

# Constants
FREEZE_COST_COINS = 50
MAX_FREEZES_PER_MONTH = 2
FREE_FREEZE_COOLDOWN_DAYS = 7
FREEZE_DURATION_HOURS = 24


class StreakStatusResponse(BaseModel):
    """Response schema for streak status."""
    current_streak: int = Field(..., description="Current streak count")
    best_streak: int = Field(..., description="Best streak ever")
    is_frozen: bool = Field(..., description="Whether streak is currently frozen")
    frozen_until: datetime | None = Field(None, description="When the freeze expires")
    free_freeze_available: bool = Field(..., description="Whether free freeze is available")
    next_free_freeze: datetime | None = Field(None, description="When next free freeze becomes available")
    freezes_used_this_month: int = Field(..., description="Number of freezes used this month")
    freezes_remaining_this_month: int = Field(..., description="Freezes remaining this month")
    coins: int = Field(..., description="User's current coin balance")
    freeze_cost: int = Field(default=FREEZE_COST_COINS, description="Cost of a paid freeze")


class FreezeResponse(BaseModel):
    """Response schema for freeze action."""
    success: bool = Field(..., description="Whether the freeze was applied")
    message: str = Field(..., description="Status message")
    was_free: bool = Field(..., description="Whether this was a free freeze")
    coins_spent: int = Field(default=0, description="Coins spent on this freeze")
    frozen_until: datetime = Field(..., description="When the freeze expires")
    freezes_remaining_this_month: int = Field(..., description="Freezes remaining this month")


def is_monday_reset_needed(last_freeze: datetime | None, now: datetime) -> bool:
    """Check if the free freeze should be reset (new week started)."""
    if last_freeze is None:
        return True
    
    # Find the most recent Monday at 00:00 UTC
    days_since_monday = now.weekday()
    current_monday = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
    
    # If last freeze was before this Monday, reset is available
    return last_freeze < current_monday


def is_new_month(last_freeze: datetime | None, now: datetime) -> bool:
    """Check if we're in a new month compared to last freeze."""
    if last_freeze is None:
        return True
    return last_freeze.year != now.year or last_freeze.month != now.month


@router.get("/status", response_model=StreakStatusResponse)
async def get_streak_status(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StreakStatusResponse:
    """
    Get current streak status and freeze availability.
    
    Returns streak info, freeze status, and availability of free/paid freezes.
    """
    now = datetime.now(timezone.utc)
    
    # Check if streak is currently frozen
    is_frozen = (
        current_user.streak_frozen_until is not None 
        and current_user.streak_frozen_until > now
    )
    
    # Check free freeze availability (reset on Monday)
    free_freeze_available = is_monday_reset_needed(current_user.last_free_freeze, now)
    
    # Calculate next free freeze date
    next_free_freeze = None
    if not free_freeze_available and current_user.last_free_freeze:
        # Next Monday at 00:00 UTC
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7  # If today is Monday, next reset is next Monday
        next_free_freeze = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
    
    # Reset monthly count if new month
    freezes_this_month = current_user.freeze_count_month
    if is_new_month(current_user.last_free_freeze, now):
        freezes_this_month = 0
    
    return StreakStatusResponse(
        current_streak=current_user.current_streak,
        best_streak=current_user.best_streak,
        is_frozen=is_frozen,
        frozen_until=current_user.streak_frozen_until if is_frozen else None,
        free_freeze_available=free_freeze_available,
        next_free_freeze=next_free_freeze,
        freezes_used_this_month=freezes_this_month,
        freezes_remaining_this_month=max(0, MAX_FREEZES_PER_MONTH - freezes_this_month),
        coins=current_user.coins,
        freeze_cost=FREEZE_COST_COINS,
    )


@router.post("/freeze", response_model=FreezeResponse)
async def apply_streak_freeze(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FreezeResponse:
    """
    Apply a streak freeze to protect the streak for 24 hours.
    
    Rules:
    - 1 free freeze per week (resets on Monday)
    - Additional freezes cost 50 coins each
    - Maximum 2 freezes per month
    - Cannot stack freezes (must wait for current to expire)
    """
    now = datetime.now(timezone.utc)
    
    # Check if already frozen
    if current_user.streak_frozen_until and current_user.streak_frozen_until > now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Streak is already frozen until {current_user.streak_frozen_until.isoformat()}",
        )
    
    # Reset monthly count if new month
    if is_new_month(current_user.last_free_freeze, now):
        current_user.freeze_count_month = 0
    
    # Check monthly limit
    if current_user.freeze_count_month >= MAX_FREEZES_PER_MONTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Monthly freeze limit reached ({MAX_FREEZES_PER_MONTH} freezes per month)",
        )
    
    # Determine if free freeze is available
    free_freeze_available = is_monday_reset_needed(current_user.last_free_freeze, now)
    
    coins_spent = 0
    was_free = False
    
    if free_freeze_available:
        # Use free freeze
        was_free = True
        current_user.last_free_freeze = now
    else:
        # Paid freeze - check coins
        if current_user.coins < FREEZE_COST_COINS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient coins. Need {FREEZE_COST_COINS}, have {current_user.coins}",
            )
        
        # Deduct coins
        current_user.coins -= FREEZE_COST_COINS
        coins_spent = FREEZE_COST_COINS
    
    # Apply the freeze
    frozen_until = now + timedelta(hours=FREEZE_DURATION_HOURS)
    current_user.streak_frozen_until = frozen_until
    current_user.freeze_count_month += 1
    
    # Commit changes
    await db.commit()
    await db.refresh(current_user)
    
    return FreezeResponse(
        success=True,
        message="Streak freeze applied successfully!" if was_free else f"Streak freeze purchased for {FREEZE_COST_COINS} coins!",
        was_free=was_free,
        coins_spent=coins_spent,
        frozen_until=frozen_until,
        freezes_remaining_this_month=max(0, MAX_FREEZES_PER_MONTH - current_user.freeze_count_month),
    )
