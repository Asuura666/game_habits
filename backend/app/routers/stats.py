"""
Stats Router - Analytics & Insights

Endpoints for user statistics:
- Overview (XP, streak, badges, level)
- Per-habit stats
- Calendar heatmap data
- Trends analysis
- AI-generated insights
- Data export
"""

import csv
import io
import json
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum
from typing import Annotated
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.badge import UserBadge
from app.models.completion import Completion
from app.models.habit import Habit
from app.models.stats import DailyStats
from app.models.user import User
from app.schemas.stats import (
    CalendarDay,
    CalendarResponse,
    HabitStat,
    Insight,
    InsightCategory,
    InsightsResponse,
    StatsOverview,
    TimeRange,
)
from app.utils.auth import CurrentUser

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter(prefix="/stats", tags=["stats"])


# ============================================================================
# Helper Functions
# ============================================================================


def get_date_range(time_range: TimeRange) -> tuple[date, date]:
    """Get start and end dates for a time range."""
    today = datetime.now(timezone.utc).date()
    
    if time_range == TimeRange.TODAY:
        return today, today
    elif time_range == TimeRange.WEEK:
        start = today - timedelta(days=today.weekday())
        return start, today
    elif time_range == TimeRange.MONTH:
        start = today.replace(day=1)
        return start, today
    elif time_range == TimeRange.YEAR:
        start = today.replace(month=1, day=1)
        return start, today
    else:  # ALL_TIME
        return date(2020, 1, 1), today


class ExportFormat(str, Enum):
    """Export format options."""
    JSON = "json"
    CSV = "csv"


# ============================================================================
# Overview
# ============================================================================


@router.get(
    "/overview",
    response_model=StatsOverview,
    summary="Stats Overview",
    description="Get comprehensive statistics overview for the user",
)
async def get_stats_overview(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    time_range: TimeRange = Query(TimeRange.WEEK),
) -> StatsOverview:
    """Get overall statistics for the user."""
    start_date, end_date = get_date_range(time_range)
    
    # Get daily stats for the period
    result = await db.execute(
        select(DailyStats).where(
            DailyStats.user_id == current_user.id,
            DailyStats.date >= start_date,
            DailyStats.date <= end_date,
        ).order_by(DailyStats.date)
    )
    daily_stats = result.scalars().all()
    
    # Calculate aggregates
    total_completions = sum(ds.habits_completed for ds in daily_stats)
    total_tasks = sum(ds.tasks_completed for ds in daily_stats)
    total_xp = sum(ds.xp_earned for ds in daily_stats)
    total_coins = sum(ds.coins_earned for ds in daily_stats)
    perfect_days = sum(1 for ds in daily_stats if ds.completion_rate == 100)
    days_with_activity = sum(1 for ds in daily_stats if ds.habits_completed > 0)
    
    # Overall completion rate
    total_scheduled = sum(ds.habits_total for ds in daily_stats)
    overall_rate = (total_completions / total_scheduled * 100) if total_scheduled > 0 else 0
    
    # Get active habits count
    habits_result = await db.execute(
        select(func.count(Habit.id)).where(
            Habit.user_id == current_user.id,
            Habit.is_archived == False,
        )
    )
    total_habits = habits_result.scalar() or 0
    
    # Best habit (highest completion rate)
    best_habit = await _get_best_habit(db, current_user.id, start_date, end_date)
    most_completed = await _get_most_completed_habit(db, current_user.id, start_date, end_date)
    
    # Calculate trend vs previous period
    period_days = (end_date - start_date).days + 1
    prev_start = start_date - timedelta(days=period_days)
    prev_end = start_date - timedelta(days=1)
    
    prev_result = await db.execute(
        select(DailyStats).where(
            DailyStats.user_id == current_user.id,
            DailyStats.date >= prev_start,
            DailyStats.date <= prev_end,
        )
    )
    prev_stats = prev_result.scalars().all()
    
    prev_scheduled = sum(ds.habits_total for ds in prev_stats)
    prev_completed = sum(ds.habits_completed for ds in prev_stats)
    prev_rate = (prev_completed / prev_scheduled * 100) if prev_scheduled > 0 else 0
    
    completion_trend = overall_rate - prev_rate
    
    prev_xp = sum(ds.xp_earned for ds in prev_stats)
    xp_trend = ((total_xp - prev_xp) / prev_xp * 100) if prev_xp > 0 else 0
    
    return StatsOverview(
        time_range=time_range,
        start_date=start_date,
        end_date=end_date,
        total_habits=total_habits,
        total_tasks_completed=total_tasks,
        total_completions=total_completions,
        total_xp_earned=total_xp,
        total_coins_earned=total_coins,
        overall_completion_rate=round(overall_rate, 1),
        perfect_days=perfect_days,
        days_with_activity=days_with_activity,
        current_streak=current_user.current_streak,
        longest_streak=current_user.best_streak,
        best_habit=best_habit,
        most_completed_habit=most_completed,
        completion_trend=round(completion_trend, 1),
        xp_trend=round(xp_trend, 1),
    )


async def _get_best_habit(
    db: AsyncSession,
    user_id: UUID,
    start_date: date,
    end_date: date,
) -> HabitStat | None:
    """Get habit with highest completion rate."""
    habits_result = await db.execute(
        select(Habit).where(
            Habit.user_id == user_id,
            Habit.is_archived == False,
        )
    )
    habits = habits_result.scalars().all()
    
    if not habits:
        return None
    
    best = None
    best_rate = -1
    
    for habit in habits:
        completions_result = await db.execute(
            select(func.count(Completion.id)).where(
                Completion.habit_id == habit.id,
                Completion.completed_date >= start_date,
                Completion.completed_date <= end_date,
            )
        )
        completions = completions_result.scalar() or 0
        
        # Calculate expected completions (simplified: daily habit)
        days = (end_date - start_date).days + 1
        rate = (completions / days * 100) if days > 0 else 0
        
        if rate > best_rate:
            best_rate = rate
            best = HabitStat(
                habit_id=habit.id,
                habit_name=habit.name,
                icon=habit.icon or "📌",
                total_completions=completions,
                current_streak=habit.current_streak,
                best_streak=habit.best_streak,
                completion_rate=round(rate, 1),
                total_xp_earned=habit.total_xp_earned,
                average_mood=None,
            )
    
    return best


async def _get_most_completed_habit(
    db: AsyncSession,
    user_id: UUID,
    start_date: date,
    end_date: date,
) -> HabitStat | None:
    """Get habit completed most often."""
    result = await db.execute(
        select(
            Completion.habit_id,
            func.count(Completion.id).label("count"),
        )
        .join(Habit, Habit.id == Completion.habit_id)
        .where(
            Habit.user_id == user_id,
            Completion.completed_date >= start_date,
            Completion.completed_date <= end_date,
        )
        .group_by(Completion.habit_id)
        .order_by(func.count(Completion.id).desc())
        .limit(1)
    )
    row = result.first()
    
    if not row:
        return None
    
    habit_id, count = row
    
    habit_result = await db.execute(
        select(Habit).where(Habit.id == habit_id)
    )
    habit = habit_result.scalar_one()
    
    days = (end_date - start_date).days + 1
    rate = (count / days * 100) if days > 0 else 0
    
    return HabitStat(
        habit_id=habit.id,
        habit_name=habit.name,
        icon=habit.icon or "📌",
        total_completions=count,
        current_streak=habit.current_streak,
        best_streak=habit.best_streak,
        completion_rate=round(rate, 1),
        total_xp_earned=habit.total_xp_earned,
        average_mood=None,
    )


# ============================================================================
# Per-Habit Stats
# ============================================================================


@router.get(
    "/habits",
    response_model=list[HabitStat],
    summary="Habit Statistics",
    description="Get detailed statistics for each habit",
)
async def get_habit_stats(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    time_range: TimeRange = Query(TimeRange.MONTH),
) -> list[HabitStat]:
    """Get statistics for all user habits."""
    start_date, end_date = get_date_range(time_range)
    
    # Get all habits
    habits_result = await db.execute(
        select(Habit).where(Habit.user_id == current_user.id)
    )
    habits = habits_result.scalars().all()
    
    stats = []
    days = (end_date - start_date).days + 1
    
    for habit in habits:
        # Count completions in period
        completions_result = await db.execute(
            select(func.count(Completion.id)).where(
                Completion.habit_id == habit.id,
                Completion.completed_date >= start_date,
                Completion.completed_date <= end_date,
            )
        )
        completions = completions_result.scalar() or 0
        
        rate = (completions / days * 100) if days > 0 else 0
        
        stats.append(HabitStat(
            habit_id=habit.id,
            habit_name=habit.name,
            icon=habit.icon or "📌",
            total_completions=completions,
            current_streak=habit.current_streak,
            best_streak=habit.best_streak,
            completion_rate=round(rate, 1),
            total_xp_earned=habit.total_xp_earned,
            average_mood=None,
        ))
    
    # Sort by completion rate descending
    stats.sort(key=lambda x: x.completion_rate, reverse=True)
    
    return stats


# ============================================================================
# Calendar Heatmap
# ============================================================================


@router.get(
    "/calendar",
    response_model=CalendarResponse,
    summary="Calendar Data",
    description="Get daily completion data for calendar heatmap",
)
async def get_calendar_data(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    year: int = Query(None),
    month: int = Query(None, ge=1, le=12),
) -> CalendarResponse:
    """Get calendar heatmap data."""
    today = datetime.now(timezone.utc).date()
    
    if year is None:
        year = today.year
    if month is None:
        month = today.month
    
    # Calculate month boundaries
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # Get daily stats for the month
    result = await db.execute(
        select(DailyStats).where(
            DailyStats.user_id == current_user.id,
            DailyStats.date >= start_date,
            DailyStats.date <= end_date,
        ).order_by(DailyStats.date)
    )
    daily_stats = result.scalars().all()
    
    # Build calendar days
    days = []
    for ds in daily_stats:
        is_perfect = ds.habits_total > 0 and ds.habits_completed == ds.habits_total
        
        days.append(CalendarDay(
            date=ds.date,
            habits_scheduled=ds.habits_total,
            habits_completed=ds.habits_completed,
            tasks_completed=ds.tasks_completed,
            total_xp=ds.xp_earned,
            total_coins=ds.coins_earned,
            completion_rate=float(ds.completion_rate),
            mood_average=None,
            is_perfect_day=is_perfect,
        ))
    
    # Calculate month stats
    month_rate = (
        sum(d.completion_rate for d in days) / len(days)
        if days else 0
    )
    perfect_count = sum(1 for d in days if d.is_perfect_day)
    total_xp = sum(d.total_xp for d in days)
    
    return CalendarResponse(
        month=month,
        year=year,
        days=days,
        month_completion_rate=round(month_rate, 1),
        perfect_days_count=perfect_count,
        total_xp=total_xp,
    )


# ============================================================================
# Trends
# ============================================================================


@router.get(
    "/trends",
    summary="Trends Analysis",
    description="Compare current week vs previous week",
)
async def get_trends(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get week-over-week trend analysis."""
    today = datetime.now(timezone.utc).date()
    
    # Current week (Mon-Sun)
    week_start = today - timedelta(days=today.weekday())
    week_end = today
    
    # Previous week
    prev_week_start = week_start - timedelta(days=7)
    prev_week_end = week_start - timedelta(days=1)
    
    # Get current week stats
    current_result = await db.execute(
        select(DailyStats).where(
            DailyStats.user_id == current_user.id,
            DailyStats.date >= week_start,
            DailyStats.date <= week_end,
        )
    )
    current_stats = current_result.scalars().all()
    
    # Get previous week stats
    prev_result = await db.execute(
        select(DailyStats).where(
            DailyStats.user_id == current_user.id,
            DailyStats.date >= prev_week_start,
            DailyStats.date <= prev_week_end,
        )
    )
    prev_stats = prev_result.scalars().all()
    
    # Calculate metrics
    def calc_metrics(stats):
        if not stats:
            return {"completions": 0, "xp": 0, "rate": 0}
        
        completions = sum(s.habits_completed for s in stats)
        total = sum(s.habits_total for s in stats)
        xp = sum(s.xp_earned for s in stats)
        rate = (completions / total * 100) if total > 0 else 0
        
        return {"completions": completions, "xp": xp, "rate": round(rate, 1)}
    
    current = calc_metrics(current_stats)
    previous = calc_metrics(prev_stats)
    
    # Calculate deltas
    def calc_delta(curr, prev):
        if prev == 0:
            return 100 if curr > 0 else 0
        return round((curr - prev) / prev * 100, 1)
    
    return {
        "current_week": {
            "start": week_start.isoformat(),
            "end": week_end.isoformat(),
            **current,
        },
        "previous_week": {
            "start": prev_week_start.isoformat(),
            "end": prev_week_end.isoformat(),
            **previous,
        },
        "trends": {
            "completions_delta": calc_delta(current["completions"], previous["completions"]),
            "xp_delta": calc_delta(current["xp"], previous["xp"]),
            "rate_delta": current["rate"] - previous["rate"],
            "improving": current["rate"] > previous["rate"],
        },
    }


# ============================================================================
# AI Insights
# ============================================================================


@router.get(
    "/insights",
    response_model=InsightsResponse,
    summary="AI Insights",
    description="Get AI-generated insights about habits (may use LLM)",
)
async def get_insights(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> InsightsResponse:
    """
    Generate insights about user's habit performance.
    
    Currently uses rule-based insights.
    Can be extended to use LLM for more sophisticated analysis.
    """
    insights = []
    now = datetime.now(timezone.utc)
    
    # Streak insights
    if current_user.current_streak >= 7:
        insights.append(Insight(
            id=uuid4(),
            category=InsightCategory.ACHIEVEMENT,
            title="🔥 On Fire!",
            message=f"You're on a {current_user.current_streak}-day streak! "
                    f"Your best ever was {current_user.best_streak} days.",
            action_suggestion="Keep going to beat your record!" if current_user.current_streak < current_user.best_streak else None,
            related_habit_id=None,
            priority=3,
            generated_at=now,
            is_read=False,
        ))
    elif current_user.current_streak == 0:
        insights.append(Insight(
            id=uuid4(),
            category=InsightCategory.MOTIVATION,
            title="💪 Fresh Start",
            message="Time to start a new streak! Complete all your habits today to begin.",
            action_suggestion="Focus on your easiest habit first",
            related_habit_id=None,
            priority=2,
            generated_at=now,
            is_read=False,
        ))
    
    # Get recent completion data
    week_ago = now.date() - timedelta(days=7)
    result = await db.execute(
        select(DailyStats).where(
            DailyStats.user_id == current_user.id,
            DailyStats.date >= week_ago,
        )
    )
    recent_stats = result.scalars().all()
    
    if recent_stats:
        avg_rate = sum(float(s.completion_rate) for s in recent_stats) / len(recent_stats)
        
        if avg_rate >= 80:
            insights.append(Insight(
                id=uuid4(),
                category=InsightCategory.ACHIEVEMENT,
                title="⭐ Consistency Champion",
                message=f"Amazing! You've averaged {avg_rate:.0f}% completion this week.",
                action_suggestion=None,
                related_habit_id=None,
                priority=2,
                generated_at=now,
                is_read=False,
            ))
        elif avg_rate < 50:
            insights.append(Insight(
                id=uuid4(),
                category=InsightCategory.SUGGESTION,
                title="🎯 Room to Grow",
                message=f"Your completion rate this week is {avg_rate:.0f}%. "
                        "Consider reducing habits or adjusting difficulty.",
                action_suggestion="Try focusing on 2-3 key habits first",
                related_habit_id=None,
                priority=3,
                generated_at=now,
                is_read=False,
            ))
    
    # Check for struggling habits
    habits_result = await db.execute(
        select(Habit).where(
            Habit.user_id == current_user.id,
            Habit.is_archived == False,
            Habit.current_streak == 0,
        )
    )
    struggling_habits = habits_result.scalars().all()
    
    for habit in struggling_habits[:2]:  # Max 2 warnings
        insights.append(Insight(
            id=uuid4(),
            category=InsightCategory.WARNING,
            title=f"⚠️ {habit.name} needs attention",
            message=f"Your streak for '{habit.name}' broke. "
                    f"Your best was {habit.best_streak} days.",
            action_suggestion="Set a reminder or make it easier to complete",
            related_habit_id=habit.id,
            priority=2,
            generated_at=now,
            is_read=False,
        ))
    
    # Sort by priority
    insights.sort(key=lambda x: x.priority, reverse=True)
    
    return InsightsResponse(
        insights=insights,
        unread_count=len(insights),
        generated_at=now,
    )


# ============================================================================
# Data Export
# ============================================================================


@router.get(
    "/export",
    summary="Export Data",
    description="Export user data as JSON or CSV",
)
async def export_data(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    format: ExportFormat = Query(ExportFormat.JSON),
    time_range: TimeRange = Query(TimeRange.ALL_TIME),
) -> Response:
    """Export user statistics data."""
    start_date, end_date = get_date_range(time_range)
    
    # Get daily stats
    stats_result = await db.execute(
        select(DailyStats).where(
            DailyStats.user_id == current_user.id,
            DailyStats.date >= start_date,
            DailyStats.date <= end_date,
        ).order_by(DailyStats.date)
    )
    daily_stats = stats_result.scalars().all()
    
    # Get habits
    habits_result = await db.execute(
        select(Habit).where(Habit.user_id == current_user.id)
    )
    habits = habits_result.scalars().all()
    
    # Get completions
    completions_result = await db.execute(
        select(Completion).where(
            Completion.user_id == current_user.id,
            Completion.completed_date >= start_date,
            Completion.completed_date <= end_date,
        )
    )
    completions = completions_result.scalars().all()
    
    if format == ExportFormat.JSON:
        # Build JSON export
        data = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "user": {
                "username": current_user.username,
                "level": current_user.level,
                "total_xp": current_user.total_xp,
                "current_streak": current_user.current_streak,
                "best_streak": current_user.best_streak,
            },
            "time_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "habits": [
                {
                    "id": str(h.id),
                    "name": h.name,
                    "icon": h.icon,
                    "current_streak": h.current_streak,
                    "best_streak": h.best_streak,
                }
                for h in habits
            ],
            "daily_stats": [
                {
                    "date": ds.date.isoformat(),
                    "habits_total": ds.habits_total,
                    "habits_completed": ds.habits_completed,
                    "completion_rate": float(ds.completion_rate),
                    "tasks_completed": ds.tasks_completed,
                    "xp_earned": ds.xp_earned,
                    "coins_earned": ds.coins_earned,
                }
                for ds in daily_stats
            ],
            "completions": [
                {
                    "habit_id": str(c.habit_id),
                    "completed_date": c.completed_date.isoformat(),
                    "xp_earned": c.xp_earned,
                }
                for c in completions
            ],
        }
        
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=habit-data-{start_date}-{end_date}.json"
            },
        )
    
    else:  # CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write daily stats
        writer.writerow([
            "date", "habits_total", "habits_completed", "completion_rate",
            "tasks_completed", "xp_earned", "coins_earned"
        ])
        
        for ds in daily_stats:
            writer.writerow([
                ds.date.isoformat(),
                ds.habits_total,
                ds.habits_completed,
                float(ds.completion_rate),
                ds.tasks_completed,
                ds.xp_earned,
                ds.coins_earned,
            ])
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=habit-data-{start_date}-{end_date}.csv"
            },
        )
