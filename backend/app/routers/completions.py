"""
Completions Router

Endpoints for tracking habit completions:
- Create completion (mark habit as done)
- Delete completion (undo)
- View today's completions
- View completion history
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.completion import Completion
from app.models.habit import Habit
from app.schemas.completion import (
    CompletionCreate,
    CompletionResponse,
    CompletionResult,
    CompletionWithResult,
    DailyCompletionSummary,
    CompletionBackfill,
    CompletionType,
)
from app.services.streak_service import update_streak, get_streak_multiplier
from app.services.xp_service import calculate_habit_xp, add_xp
from app.utils.dependencies import CurrentUser

logger = structlog.get_logger()
router = APIRouter(prefix="/completions", tags=["Completions"])


@router.post(
    "/",
    response_model=CompletionWithResult,
    status_code=status.HTTP_201_CREATED,
    summary="Mark habit as done",
    description="Create a completion record for a habit, calculates XP, coins, and streak bonuses",
)
async def create_completion(
    completion_data: CompletionCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> CompletionWithResult:
    """Mark a habit as completed for today."""
    # Validate that habit_id is provided
    if not completion_data.habit_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="habit_id is required",
        )
    
    # Fetch the habit and verify ownership
    result = await db.execute(
        select(Habit).where(
            and_(
                Habit.id == completion_data.habit_id,
                Habit.user_id == current_user.id,
            )
        )
    )
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )
    
    if habit.is_archived:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot complete an archived habit",
        )
    
    # Check if already completed today
    today = date.today()
    existing_result = await db.execute(
        select(Completion).where(
            and_(
                Completion.habit_id == habit.id,
                Completion.completed_date == today,
            )
        )
    )
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Habit already completed today",
        )
    
    # Calculate XP for this habit completion
    xp_earned = calculate_habit_xp(current_user, habit)
    coins_earned = int(xp_earned * 0.5)  # Coins = 50% of XP
    
    # Get streak multiplier for display
    streak_multiplier = get_streak_multiplier(current_user.current_streak)
    
    # Create completion record
    completion = Completion(
        habit_id=habit.id,
        user_id=current_user.id,
        completed_date=today,
        value=1,
        note=completion_data.notes,
        xp_earned=xp_earned,
        coins_earned=coins_earned,
        streak_multiplier=Decimal(str(streak_multiplier)),
    )
    
    db.add(completion)
    
    # Update habit completion count
    habit.total_completions += 1
    habit.total_xp_earned += xp_earned
    
    # Add XP to user (this handles level up checks)
    # Note: Using sync session for service compatibility
    add_xp(
        db=db,  # type: ignore - async session compatibility
        user=current_user,
        amount=xp_earned,
        source_type="habit",
        source_id=habit.id,
        description=f"Completed habit: {habit.name}",
    )
    
    # Add coins
    current_user.coins += coins_earned
    
    # Update streak using the new service
    streak_result = await update_streak(db, current_user, today)
    new_streak = streak_result["new_streak"]
    
    # Update habit streak
    habit.current_streak = new_streak
    if new_streak > habit.best_streak:
        habit.best_streak = new_streak
    
    await db.commit()
    await db.refresh(completion)
    
    logger.info(
        "Habit completed",
        habit_id=str(habit.id),
        user_id=str(current_user.id),
        streak=new_streak,
        xp_earned=xp_earned,
    )
    
    # Build completion result
    base_xp = 10  # Base XP before multipliers
    base_coins = 5
    streak_bonus_xp = xp_earned - base_xp
    streak_bonus_coins = coins_earned - base_coins
    
    completion_result = CompletionResult(
        xp_earned=xp_earned,
        coins_earned=coins_earned,
        base_xp=base_xp,
        base_coins=base_coins,
        streak_multiplier=float(streak_multiplier),
        streak_bonus_xp=max(0, streak_bonus_xp),
        streak_bonus_coins=max(0, streak_bonus_coins),
        new_streak=new_streak,
        is_personal_best=streak_result.get("new_streak", 0) > streak_result.get("old_streak", 0) and new_streak > current_user.best_streak,
        level_up=False,  # Would need to track from add_xp
        new_level=None,
        badges_earned=[b.code for b in streak_result.get("badges_earned", [])],
        achievement_message=f"🔥 {new_streak}-day streak!" if new_streak >= 7 else None,
    )
    
    return CompletionWithResult(
        id=completion.id,
        user_id=completion.user_id,
        completion_type="habit",
        habit_id=completion.habit_id,
        task_id=None,
        xp_earned=completion.xp_earned,
        coins_earned=completion.coins_earned,
        streak_at_completion=new_streak,
        notes=completion.note,
        mood_rating=completion_data.mood_rating,
        difficulty_rating=completion_data.difficulty_rating,
        completed_at=completion.created_at,
        result=completion_result,
    )


@router.delete(
    "/{completion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete completion",
    description="Delete a completion record (undo a habit completion)",
)
async def delete_completion(
    completion_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a completion (undo)."""
    result = await db.execute(
        select(Completion).where(
            and_(
                Completion.id == completion_id,
                Completion.user_id == current_user.id,
            )
        )
    )
    completion = result.scalar_one_or_none()
    
    if not completion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Completion not found",
        )
    
    # Revert XP and coins
    current_user.total_xp = max(0, current_user.total_xp - completion.xp_earned)
    current_user.coins = max(0, current_user.coins - completion.coins_earned)
    
    # Fetch habit to update stats
    habit_result = await db.execute(
        select(Habit).where(Habit.id == completion.habit_id)
    )
    habit = habit_result.scalar_one_or_none()
    
    if habit:
        habit.total_completions = max(0, habit.total_completions - 1)
        # Streak recalculation would be complex, simplified here
        # In production, we'd recalculate the full streak
        if completion.completed_date == date.today():
            # Only reset if we're undoing today's completion
            # Need to recalculate streak properly
            pass
    
    await db.delete(completion)
    await db.commit()
    
    logger.info(
        "Completion deleted",
        completion_id=str(completion_id),
        user_id=str(current_user.id),
        xp_reverted=completion.xp_earned,
    )




@router.post(
    "/backfill",
    response_model=CompletionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Backfill a past completion",
    description="Add a completion for a past date (max 30 days ago). XP reduced by 50%.",
)
async def backfill_completion(
    data: CompletionBackfill,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> CompletionResponse:
    """Backfill a habit completion for a past date."""
    from datetime import timedelta
    
    today_date = date.today()
    if data.completed_date > today_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot complete habits in the future",
        )
    
    max_past = today_date - timedelta(days=30)
    if data.completed_date < max_past:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only backfill completions from the last 30 days",
        )
    
    result = await db.execute(
        select(Habit).where(
            and_(Habit.id == data.habit_id, Habit.user_id == current_user.id)
        )
    )
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    
    existing = await db.execute(
        select(Completion).where(
            and_(Completion.habit_id == habit.id, Completion.completed_date == data.completed_date)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Habit already completed on {data.completed_date}",
        )
    
    base_xp = 10  # Default XP for backfill
    xp_earned = int(base_xp * 0.5)
    coins_earned = int(xp_earned * 0.5)
    
    completion = Completion(
        habit_id=habit.id,
        user_id=current_user.id,
        completed_date=data.completed_date,
        value=1,
        note=data.notes,
        xp_earned=xp_earned,
        coins_earned=coins_earned,
        streak_multiplier=Decimal("1.0"),
    )
    
    db.add(completion)
    current_user.total_xp += xp_earned
    current_user.coins += coins_earned
    habit.total_completions += 1
    
    await db.commit()
    await db.refresh(completion)
    
    logger.info("Backfill created", habit_id=str(habit.id), date=str(data.completed_date))
    
    return CompletionResponse(
        id=completion.id,
        user_id=completion.user_id,
        completion_type=CompletionType.HABIT,
        habit_id=completion.habit_id,
        task_id=None,
        xp_earned=completion.xp_earned,
        coins_earned=completion.coins_earned,
        streak_at_completion=0,
        notes=completion.note,
        mood_rating=None,
        difficulty_rating=None,
        completed_at=datetime.combine(completion.completed_date, datetime.min.time()),
    )

@router.get(
    "/today",
    response_model=list[CompletionResponse],
    summary="Today's completions",
    description="Get all completions for today",
)
async def get_today_completions(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[CompletionResponse]:
    """Get all completions for today."""
    today = date.today()
    
    result = await db.execute(
        select(Completion)
        .where(
            and_(
                Completion.user_id == current_user.id,
                Completion.completed_date == today,
            )
        )
        .order_by(Completion.created_at.desc())
    )
    completions = result.scalars().all()
    
    return [
        CompletionResponse(
            id=c.id,
            user_id=c.user_id,
            completion_type="habit",
            habit_id=c.habit_id,
            task_id=None,
            xp_earned=c.xp_earned,
            coins_earned=c.coins_earned,
            streak_at_completion=0,  # Would need to track this
            notes=c.note,
            mood_rating=None,
            difficulty_rating=None,
            completed_at=c.created_at,
        )
        for c in completions
    ]


@router.get(
    "/history",
    response_model=list[CompletionResponse],
    summary="Completion history",
    description="Get completion history with optional date filtering",
)
async def get_completion_history(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    habit_id: Optional[UUID] = Query(None, description="Filter by habit"),
    limit: int = Query(50, ge=1, le=365, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> list[CompletionResponse]:
    """Get completion history with filters."""
    query = select(Completion).where(Completion.user_id == current_user.id)
    
    if start_date:
        query = query.where(Completion.completed_date >= start_date)
    if end_date:
        query = query.where(Completion.completed_date <= end_date)
    if habit_id:
        query = query.where(Completion.habit_id == habit_id)
    
    query = query.order_by(Completion.completed_date.desc(), Completion.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    completions = result.scalars().all()
    
    return [
        CompletionResponse(
            id=c.id,
            user_id=c.user_id,
            completion_type="habit",
            habit_id=c.habit_id,
            task_id=None,
            xp_earned=c.xp_earned,
            coins_earned=c.coins_earned,
            streak_at_completion=0,
            notes=c.note,
            mood_rating=None,
            difficulty_rating=None,
            completed_at=c.created_at,
        )
        for c in completions
    ]


@router.get(
    "/summary",
    response_model=list[DailyCompletionSummary],
    summary="Daily summaries",
    description="Get daily completion summaries for a date range",
)
async def get_daily_summaries(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=90, description="Number of days to include"),
) -> list[DailyCompletionSummary]:
    """Get daily completion summaries."""
    today = date.today()
    start_date = today - timedelta(days=days - 1)
    
    # Get completions grouped by date
    result = await db.execute(
        select(
            Completion.completed_date,
            func.count(Completion.id).label("count"),
            func.sum(Completion.xp_earned).label("total_xp"),
            func.sum(Completion.coins_earned).label("total_coins"),
        )
        .where(
            and_(
                Completion.user_id == current_user.id,
                Completion.completed_date >= start_date,
                Completion.completed_date <= today,
            )
        )
        .group_by(Completion.completed_date)
        .order_by(Completion.completed_date.desc())
    )
    completion_stats = {row[0]: row for row in result.fetchall()}
    
    # Get total habits for each day (simplified - counts all non-archived habits)
    habit_count_result = await db.execute(
        select(func.count(Habit.id))
        .where(
            and_(
                Habit.user_id == current_user.id,
                Habit.is_archived == False,
            )
        )
    )
    total_habits = habit_count_result.scalar() or 0
    
    # Build summaries for each day
    summaries = []
    current_date = today
    
    while current_date >= start_date:
        stats = completion_stats.get(current_date)
        
        if stats:
            habits_completed = stats[1]
            total_xp = stats[2] or 0
            total_coins = stats[3] or 0
            completion_rate = (habits_completed / total_habits * 100) if total_habits > 0 else 0
        else:
            habits_completed = 0
            total_xp = 0
            total_coins = 0
            completion_rate = 0
        
        summaries.append(DailyCompletionSummary(
            date=datetime.combine(current_date, datetime.min.time()),
            habits_completed=habits_completed,
            habits_total=total_habits,
            tasks_completed=0,  # Would need separate tracking
            total_xp=total_xp,
            total_coins=total_coins,
            completion_rate=round(completion_rate, 1),
        ))
        
        current_date -= timedelta(days=1)
    
    return summaries
