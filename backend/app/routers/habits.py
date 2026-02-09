"""
Habits Router

Endpoints for managing recurring habits:
- CRUD operations for habits
- Today's habits with frequency logic
- Habit history and archiving
"""

from datetime import date, datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.completion import Completion
from app.models.habit import Habit
from app.schemas.habit import (
    DayOfWeek,
    Frequency,
    HabitCreate,
    HabitResponse,
    HabitUpdate,
    HabitWithProgress,
)
from app.schemas.completion import CompletionResponse
from app.utils.dependencies import CurrentUser


def should_show_on_date(habit: Habit, target_date: date) -> bool:
    """
    Determine if a habit should be shown/tracked on a specific date.
    
    Args:
        habit: The habit to check
        target_date: The date to check
    
    Returns:
        True if habit should appear on this date
    """
    if habit.is_archived:
        return False
    
    if habit.frequency_type == "daily":
        return True
    
    if habit.frequency_type == "weekly":
        # Show on first day of week (Monday = 0)
        return target_date.weekday() == 0
    
    if habit.frequency_type == "specific_days":
        # frequency_days contains weekday indices (0=Mon, 6=Sun)
        return target_date.weekday() in (habit.frequency_days or [])
    
    if habit.frequency_type == "x_per_week":
        # For x_per_week, always show until target met
        return True
    
    return True

logger = structlog.get_logger()
router = APIRouter(prefix="/habits", tags=["Habits"])


# Helper to map schema enums to model values
FREQUENCY_MAP = {
    Frequency.DAILY: "daily",
    Frequency.WEEKLY: "weekly",
    Frequency.SPECIFIC_DAYS: "specific_days",
    Frequency.X_PER_WEEK: "x_per_week",
}

DAY_TO_INT = {
    DayOfWeek.MONDAY: 0,
    DayOfWeek.TUESDAY: 1,
    DayOfWeek.WEDNESDAY: 2,
    DayOfWeek.THURSDAY: 3,
    DayOfWeek.FRIDAY: 4,
    DayOfWeek.SATURDAY: 5,
    DayOfWeek.SUNDAY: 6,
}


def habit_to_response(habit: Habit, completed_today: bool = False) -> HabitResponse:
    """Convert Habit model to HabitResponse schema."""
    return HabitResponse(
        id=habit.id,
        user_id=habit.user_id,
        title=habit.name,
        description=habit.description,
        icon=habit.icon,
        color=habit.color,
        frequency=habit.frequency_type,
        specific_days=[list(DAY_TO_INT.keys())[list(DAY_TO_INT.values()).index(d)] for d in (habit.frequency_days or [])],
        times_per_week=habit.frequency_count,
        reminder_time=habit.reminder_time,
        base_xp=10,  # Default, could be stored in model
        base_coins=5,  # Default
        current_streak=habit.current_streak,
        best_streak=habit.best_streak,
        total_completions=habit.total_completions,
        is_active=not habit.is_archived,
        completed_today=completed_today,
        created_at=habit.created_at,
        updated_at=habit.updated_at,
    )


@router.get(
    "/",
    response_model=list[HabitResponse],
    summary="List my habits",
    description="Get all habits for the authenticated user",
)
async def list_habits(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    include_archived: bool = Query(False, description="Include archived habits"),
    category: Optional[str] = Query(None, description="Filter by category"),
) -> list[HabitResponse]:
    """List all habits for the current user."""
    query = select(Habit).where(Habit.user_id == current_user.id)
    
    if not include_archived:
        query = query.where(Habit.is_archived == False)
    
    if category:
        query = query.where(Habit.category == category)
    
    query = query.order_by(Habit.position, Habit.created_at)
    
    result = await db.execute(query)
    habits = result.scalars().all()
    
    # Check today's completions
    today = date.today()
    completion_result = await db.execute(
        select(Completion.habit_id)
        .where(
            and_(
                Completion.user_id == current_user.id,
                Completion.completed_date == today,
            )
        )
    )
    completed_habit_ids = {row[0] for row in completion_result.fetchall()}
    
    return [
        habit_to_response(habit, completed_today=habit.id in completed_habit_ids)
        for habit in habits
    ]


@router.post(
    "/",
    response_model=HabitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create habit",
    description="Create a new habit for the authenticated user",
)
async def create_habit(
    habit_data: HabitCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> HabitResponse:
    """Create a new habit."""
    # Get max position for ordering
    result = await db.execute(
        select(func.max(Habit.position)).where(Habit.user_id == current_user.id)
    )
    max_position = result.scalar() or 0
    
    # Convert specific_days to int list
    frequency_days = []
    if habit_data.specific_days:
        frequency_days = [DAY_TO_INT[day] for day in habit_data.specific_days]
    
    habit = Habit(
        user_id=current_user.id,
        name=habit_data.title,
        description=habit_data.description,
        icon=habit_data.icon,
        color=habit_data.color,
        frequency_type=FREQUENCY_MAP.get(habit_data.frequency, "daily"),
        frequency_days=frequency_days,
        frequency_count=habit_data.times_per_week,
        reminder_time=habit_data.reminder_time,
        reminder_enabled=habit_data.reminder_time is not None,
        position=max_position + 1,
    )
    
    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    
    logger.info(
        "Habit created",
        habit_id=str(habit.id),
        user_id=str(current_user.id),
        title=habit.name,
    )
    
    return habit_to_response(habit)


@router.get(
    "/today",
    response_model=list[HabitWithProgress],
    summary="Today's habits",
    description="Get habits scheduled for today with progress information",
)
async def get_today_habits(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[HabitWithProgress]:
    """Get habits for today based on frequency settings."""
    today = date.today()
    
    # Get all active habits
    result = await db.execute(
        select(Habit)
        .where(
            and_(
                Habit.user_id == current_user.id,
                Habit.is_archived == False,
            )
        )
        .order_by(Habit.position, Habit.created_at)
    )
    all_habits = result.scalars().all()
    
    # Filter habits that should show today
    today_habits = [h for h in all_habits if should_show_on_date(h, today)]
    
    # Get today's completions
    completion_result = await db.execute(
        select(Completion.habit_id)
        .where(
            and_(
                Completion.user_id == current_user.id,
                Completion.completed_date == today,
            )
        )
    )
    completed_habit_ids = {row[0] for row in completion_result.fetchall()}
    
    # Get week completions for progress
    week_start = today - timedelta(days=today.weekday())
    week_completions_result = await db.execute(
        select(Completion.habit_id, func.count(Completion.id))
        .where(
            and_(
                Completion.user_id == current_user.id,
                Completion.completed_date >= week_start,
                Completion.completed_date <= today,
            )
        )
        .group_by(Completion.habit_id)
    )
    week_completions_map = dict(week_completions_result.fetchall())
    
    responses = []
    for habit in today_habits:
        # Calculate week target based on frequency
        if habit.frequency_type == "daily":
            week_target = 7
        elif habit.frequency_type == "x_per_week":
            week_target = habit.frequency_count or 3
        elif habit.frequency_type == "specific_days":
            week_target = len(habit.frequency_days or [])
        else:
            week_target = 1
        
        week_completions = week_completions_map.get(habit.id, 0)
        progress = min((week_completions / week_target) * 100, 100) if week_target > 0 else 0
        
        response = HabitWithProgress(
            id=habit.id,
            user_id=habit.user_id,
            title=habit.name,
            description=habit.description,
            icon=habit.icon,
            color=habit.color,
            frequency=habit.frequency_type,
            specific_days=[list(DAY_TO_INT.keys())[list(DAY_TO_INT.values()).index(d)] for d in (habit.frequency_days or [])],
            times_per_week=habit.frequency_count,
            reminder_time=habit.reminder_time,
            base_xp=10,
            base_coins=5,
            current_streak=habit.current_streak,
            best_streak=habit.best_streak,
            total_completions=habit.total_completions,
            is_active=True,
            completed_today=habit.id in completed_habit_ids,
            created_at=habit.created_at,
            updated_at=habit.updated_at,
            week_completions=week_completions,
            week_target=week_target,
            progress_percentage=round(progress, 1),
        )
        responses.append(response)
    
    return responses


@router.get(
    "/{habit_id}",
    response_model=HabitResponse,
    summary="Get habit details",
    description="Get details of a specific habit",
)
async def get_habit(
    habit_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> HabitResponse:
    """Get a specific habit by ID."""
    result = await db.execute(
        select(Habit).where(
            and_(
                Habit.id == habit_id,
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
    
    # Check if completed today
    today = date.today()
    completion_result = await db.execute(
        select(Completion.id)
        .where(
            and_(
                Completion.habit_id == habit_id,
                Completion.completed_date == today,
            )
        )
        .limit(1)
    )
    completed_today = completion_result.scalar_one_or_none() is not None
    
    return habit_to_response(habit, completed_today)


@router.put(
    "/{habit_id}",
    response_model=HabitResponse,
    summary="Update habit",
    description="Update an existing habit",
)
async def update_habit(
    habit_id: UUID,
    habit_data: HabitUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> HabitResponse:
    """Update an existing habit."""
    result = await db.execute(
        select(Habit).where(
            and_(
                Habit.id == habit_id,
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
    
    # Update fields
    update_data = habit_data.model_dump(exclude_unset=True)
    
    if "title" in update_data:
        habit.name = update_data["title"]
    if "description" in update_data:
        habit.description = update_data["description"]
    if "icon" in update_data:
        habit.icon = update_data["icon"]
    if "color" in update_data:
        habit.color = update_data["color"]
    if "frequency" in update_data and update_data["frequency"]:
        habit.frequency_type = FREQUENCY_MAP.get(update_data["frequency"], habit.frequency_type)
    if "specific_days" in update_data and update_data["specific_days"] is not None:
        habit.frequency_days = [DAY_TO_INT[day] for day in update_data["specific_days"]]
    if "times_per_week" in update_data:
        habit.frequency_count = update_data["times_per_week"]
    if "reminder_time" in update_data:
        habit.reminder_time = update_data["reminder_time"]
        habit.reminder_enabled = update_data["reminder_time"] is not None
    if "is_active" in update_data:
        habit.is_archived = not update_data["is_active"]
        if habit.is_archived:
            habit.archived_at = datetime.now(timezone.utc)
        else:
            habit.archived_at = None
    
    habit.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(habit)
    
    logger.info(
        "Habit updated",
        habit_id=str(habit.id),
        user_id=str(current_user.id),
    )
    
    return habit_to_response(habit)


@router.delete(
    "/{habit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete habit",
    description="Permanently delete a habit and all its completions",
)
async def delete_habit(
    habit_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a habit permanently."""
    result = await db.execute(
        select(Habit).where(
            and_(
                Habit.id == habit_id,
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
    
    await db.delete(habit)
    await db.commit()
    
    logger.info(
        "Habit deleted",
        habit_id=str(habit_id),
        user_id=str(current_user.id),
    )


@router.post(
    "/{habit_id}/archive",
    response_model=HabitResponse,
    summary="Archive habit",
    description="Archive a habit (soft delete, preserves history)",
)
async def archive_habit(
    habit_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> HabitResponse:
    """Archive a habit."""
    result = await db.execute(
        select(Habit).where(
            and_(
                Habit.id == habit_id,
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
    
    habit.is_archived = True
    habit.archived_at = datetime.now(timezone.utc)
    habit.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(habit)
    
    logger.info(
        "Habit archived",
        habit_id=str(habit.id),
        user_id=str(current_user.id),
    )
    
    return habit_to_response(habit)


@router.get(
    "/{habit_id}/history",
    response_model=list[CompletionResponse],
    summary="Habit completion history",
    description="Get completion history for a specific habit",
)
async def get_habit_history(
    habit_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(30, ge=1, le=365, description="Number of completions to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> list[CompletionResponse]:
    """Get completion history for a habit."""
    # Verify habit ownership
    habit_result = await db.execute(
        select(Habit.id).where(
            and_(
                Habit.id == habit_id,
                Habit.user_id == current_user.id,
            )
        )
    )
    if not habit_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )
    
    # Get completions
    result = await db.execute(
        select(Completion)
        .where(Completion.habit_id == habit_id)
        .order_by(Completion.completed_date.desc())
        .offset(offset)
        .limit(limit)
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
