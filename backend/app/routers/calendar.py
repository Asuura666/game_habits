"""Calendar Router - Heatmap data for completions."""

import calendar as cal
from datetime import date, timedelta
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.completion import Completion
from app.models.habit import Habit
from app.schemas.calendar import CalendarDayData, CalendarResponse, CalendarSummary
from app.utils.dependencies import CurrentUser

logger = structlog.get_logger()
router = APIRouter(prefix="/completions", tags=["Calendar"])


@router.get(
    "/calendar",
    response_model=CalendarResponse,
    summary="Calendar heatmap data",
    description="Get monthly completion data for calendar heatmap visualization",
)
async def get_calendar_data(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    month: Optional[str] = Query(
        None, 
        pattern=r"^\d{4}-\d{2}$",
        description="Month in YYYY-MM format (defaults to current month)",
        examples=["2026-02"]
    ),
) -> CalendarResponse:
    """Get calendar heatmap data for a specific month."""
    # Parse month or use current
    if month:
        try:
            year, month_num = map(int, month.split("-"))
            target_date = date(year, month_num, 1)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid month format. Use YYYY-MM",
            )
    else:
        today = date.today()
        target_date = date(today.year, today.month, 1)
        month = target_date.strftime("%Y-%m")
    
    # Get first and last day of month
    _, last_day = cal.monthrange(target_date.year, target_date.month)
    month_start = target_date
    month_end = date(target_date.year, target_date.month, last_day)
    
    # Get total active habits count (non-archived)
    habits_result = await db.execute(
        select(func.count(Habit.id))
        .where(
            and_(
                Habit.user_id == current_user.id,
                Habit.is_archived == False,
            )
        )
    )
    total_habits = habits_result.scalar() or 0
    
    # Get completions grouped by date for the month
    completions_result = await db.execute(
        select(
            Completion.completed_date,
            func.count(Completion.id).label("habits_done"),
            func.sum(Completion.xp_earned).label("xp_earned"),
        )
        .where(
            and_(
                Completion.user_id == current_user.id,
                Completion.completed_date >= month_start,
                Completion.completed_date <= month_end,
            )
        )
        .group_by(Completion.completed_date)
    )
    completion_data = {row[0]: (row[1], row[2] or 0) for row in completions_result.fetchall()}
    
    # Build daily data for each day of the month
    days: list[CalendarDayData] = []
    perfect_days = 0
    total_completions = 0
    rates_sum = 0.0
    days_with_habits = 0
    
    current_date = month_start
    today = date.today()
    
    while current_date <= month_end:
        habits_done, xp_earned = completion_data.get(current_date, (0, 0))
        
        # Calculate completion rate
        if total_habits > 0:
            completion_rate = habits_done / total_habits
        else:
            completion_rate = 0.0
        
        # Only count stats for days up to today
        if current_date <= today:
            total_completions += habits_done
            if total_habits > 0:
                rates_sum += completion_rate
                days_with_habits += 1
                if completion_rate >= 1.0:
                    perfect_days += 1
        
        days.append(CalendarDayData(
            day_date=current_date,
            completion_rate=round(completion_rate, 2),
            habits_done=habits_done,
            habits_total=total_habits,
            xp_earned=xp_earned,
        ))
        
        current_date += timedelta(days=1)
    
    # Calculate average rate
    average_rate = rates_sum / days_with_habits if days_with_habits > 0 else 0.0
    
    summary = CalendarSummary(
        perfect_days=perfect_days,
        total_completions=total_completions,
        average_rate=round(average_rate, 2),
    )
    
    logger.info(
        "Calendar data retrieved",
        user_id=str(current_user.id),
        month=month,
        perfect_days=perfect_days,
    )
    
    return CalendarResponse(
        month=month,
        days=days,
        summary=summary,
    )
