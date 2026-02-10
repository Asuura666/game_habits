"""
Leaderboard Router - Competitive Rankings

Friends-only leaderboards for:
- XP (weekly/monthly)
- Streak
- Completion rate
- PvP win ratio

Uses Redis sorted sets for performance when available,
falls back to SQL queries with caching.
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

import redis.asyncio as redis
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.combat import Combat
from app.models.completion import Completion
from app.models.friendship import Friendship
from app.models.habit import Habit
from app.models.stats import DailyStats
from app.models.user import User
from app.schemas.stats import (
    LeaderboardEntry,
    LeaderboardResponse,
    TimeRange,
)
from app.deps import CurrentUser

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


# ============================================================================
# Helper Functions
# ============================================================================


async def get_friend_ids_with_self(db: AsyncSession, user_id: UUID) -> list[UUID]:
    """Get list of friend user IDs including the user themselves."""
    result = await db.execute(
        select(Friendship).where(
            and_(
                or_(
                    Friendship.requester_id == user_id,
                    Friendship.addressee_id == user_id,
                ),
                Friendship.status == "accepted",
            )
        )
    )
    friendships = result.scalars().all()
    
    friend_ids = [user_id]  # Include self
    for f in friendships:
        friend_id = f.addressee_id if f.requester_id == user_id else f.requester_id
        friend_ids.append(friend_id)
    
    return friend_ids


async def get_redis_client() -> redis.Redis | None:
    """Get Redis client, return None if unavailable."""
    try:
        client = redis.from_url(settings.redis_url)
        await client.ping()
        return client
    except Exception as e:
        logger.warning("Redis unavailable, using SQL fallback", error=str(e))
        return None


def build_leaderboard_entry(
    user: User,
    rank: int,
    score: float,
    metric_label: str,
    current_user_id: UUID,
) -> LeaderboardEntry:
    """Build a LeaderboardEntry from a User."""
    return LeaderboardEntry(
        rank=rank,
        user_id=user.id,
        username=user.username,
        avatar_url=user.avatar_url,
        character_name=user.character.name if user.character else None,
        character_class=user.character.character_class if user.character else None,
        level=user.level,
        score=int(score),
        metric_value=score,
        metric_label=metric_label,
        is_current_user=user.id == current_user_id,
        is_friend=user.id != current_user_id,
    )


# ============================================================================
# XP Leaderboards
# ============================================================================


@router.get(
    "/xp/weekly",
    response_model=LeaderboardResponse,
    summary="Weekly XP Leaderboard",
    description="Get friends leaderboard by XP earned this week",
)
async def get_weekly_xp_leaderboard(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
) -> LeaderboardResponse:
    """Get weekly XP leaderboard among friends."""
    friend_ids = await get_friend_ids_with_self(db, current_user.id)
    
    # Calculate week start (Monday)
    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=today.weekday())
    
    # Aggregate XP from daily stats
    result = await db.execute(
        select(
            DailyStats.user_id,
            func.sum(DailyStats.xp_earned).label("total_xp"),
        )
        .where(
            DailyStats.user_id.in_(friend_ids),
            DailyStats.date >= week_start,
        )
        .group_by(DailyStats.user_id)
        .order_by(func.sum(DailyStats.xp_earned).desc())
        .limit(limit)
    )
    rankings = result.all()
    
    # Build entries
    entries = []
    user_rank = None
    
    for rank, (user_id, total_xp) in enumerate(rankings, 1):
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if user:
            entry = build_leaderboard_entry(
                user, rank, float(total_xp or 0), "XP", current_user.id
            )
            entries.append(entry)
            
            if user_id == current_user.id:
                user_rank = rank
    
    return LeaderboardResponse(
        leaderboard_type="xp",
        time_range=TimeRange.WEEK,
        entries=entries,
        user_rank=user_rank,
        total_participants=len(friend_ids),
        updated_at=datetime.now(timezone.utc),
    )


@router.get(
    "/xp/monthly",
    response_model=LeaderboardResponse,
    summary="Monthly XP Leaderboard",
    description="Get friends leaderboard by XP earned this month",
)
async def get_monthly_xp_leaderboard(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
) -> LeaderboardResponse:
    """Get monthly XP leaderboard among friends."""
    friend_ids = await get_friend_ids_with_self(db, current_user.id)
    
    # Calculate month start
    today = datetime.now(timezone.utc).date()
    month_start = today.replace(day=1)
    
    # Aggregate XP from daily stats
    result = await db.execute(
        select(
            DailyStats.user_id,
            func.sum(DailyStats.xp_earned).label("total_xp"),
        )
        .where(
            DailyStats.user_id.in_(friend_ids),
            DailyStats.date >= month_start,
        )
        .group_by(DailyStats.user_id)
        .order_by(func.sum(DailyStats.xp_earned).desc())
        .limit(limit)
    )
    rankings = result.all()
    
    # Build entries
    entries = []
    user_rank = None
    
    for rank, (user_id, total_xp) in enumerate(rankings, 1):
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if user:
            entry = build_leaderboard_entry(
                user, rank, float(total_xp or 0), "XP", current_user.id
            )
            entries.append(entry)
            
            if user_id == current_user.id:
                user_rank = rank
    
    return LeaderboardResponse(
        leaderboard_type="xp",
        time_range=TimeRange.MONTH,
        entries=entries,
        user_rank=user_rank,
        total_participants=len(friend_ids),
        updated_at=datetime.now(timezone.utc),
    )


# ============================================================================
# Streak Leaderboard
# ============================================================================


@router.get(
    "/streak",
    response_model=LeaderboardResponse,
    summary="Streak Leaderboard",
    description="Get friends leaderboard by current streak",
)
async def get_streak_leaderboard(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
) -> LeaderboardResponse:
    """Get streak leaderboard among friends."""
    friend_ids = await get_friend_ids_with_self(db, current_user.id)
    
    # Get users ordered by current streak
    result = await db.execute(
        select(User)
        .where(User.id.in_(friend_ids))
        .order_by(User.current_streak.desc())
        .limit(limit)
    )
    users = result.scalars().all()
    
    # Build entries
    entries = []
    user_rank = None
    
    for rank, user in enumerate(users, 1):
        entry = build_leaderboard_entry(
            user, rank, float(user.current_streak), "Streak Days", current_user.id
        )
        entries.append(entry)
        
        if user.id == current_user.id:
            user_rank = rank
    
    return LeaderboardResponse(
        leaderboard_type="streak",
        time_range=TimeRange.ALL_TIME,
        entries=entries,
        user_rank=user_rank,
        total_participants=len(friend_ids),
        updated_at=datetime.now(timezone.utc),
    )


# ============================================================================
# Completion Rate Leaderboard
# ============================================================================


@router.get(
    "/completion",
    response_model=LeaderboardResponse,
    summary="Completion Rate Leaderboard",
    description="Get friends leaderboard by habit completion rate (last 30 days)",
)
async def get_completion_leaderboard(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
) -> LeaderboardResponse:
    """Get completion rate leaderboard among friends (last 30 days)."""
    friend_ids = await get_friend_ids_with_self(db, current_user.id)
    
    # Calculate date range
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=30)
    
    # Aggregate completion rates from daily stats
    result = await db.execute(
        select(
            DailyStats.user_id,
            func.avg(DailyStats.habits_completed * 100.0 / func.nullif(DailyStats.habits_total, 0)).label("avg_completion"),
        )
        .where(
            DailyStats.user_id.in_(friend_ids),
            DailyStats.date >= start_date,
            DailyStats.habits_total > 0,  # Only count days with habits
        )
        .group_by(DailyStats.user_id)
        .order_by(func.avg(DailyStats.habits_completed * 100.0 / func.nullif(DailyStats.habits_total, 0)).desc())
        .limit(limit)
    )
    rankings = result.all()
    
    # Build entries
    entries = []
    user_rank = None
    
    for rank, (user_id, avg_completion) in enumerate(rankings, 1):
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if user:
            entry = build_leaderboard_entry(
                user, rank, float(avg_completion or 0), "Completion %", current_user.id
            )
            entries.append(entry)
            
            if user_id == current_user.id:
                user_rank = rank
    
    return LeaderboardResponse(
        leaderboard_type="completion",
        time_range=TimeRange.MONTH,
        entries=entries,
        user_rank=user_rank,
        total_participants=len(friend_ids),
        updated_at=datetime.now(timezone.utc),
    )


# ============================================================================
# PvP Leaderboard
# ============================================================================


@router.get(
    "/pvp",
    response_model=LeaderboardResponse,
    summary="PvP Leaderboard",
    description="Get friends leaderboard by PvP win ratio",
)
async def get_pvp_leaderboard(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
) -> LeaderboardResponse:
    """Get PvP win ratio leaderboard among friends."""
    friend_ids = await get_friend_ids_with_self(db, current_user.id)
    
    # Calculate win ratios from combats table
    # Using subqueries for wins and total combats
    
    rankings = []
    
    for user_id in friend_ids:
        # Count wins
        wins_result = await db.execute(
            select(func.count(Combat.id)).where(
                Combat.winner_id == user_id,
                Combat.status == "completed",
            )
        )
        wins = wins_result.scalar() or 0
        
        # Count total combats
        total_result = await db.execute(
            select(func.count(Combat.id)).where(
                or_(
                    Combat.challenger_id == user_id,
                    Combat.defender_id == user_id,
                ),
                Combat.status == "completed",
            )
        )
        total = total_result.scalar() or 0
        
        # Calculate ratio
        win_ratio = (wins / total * 100) if total > 0 else 0
        rankings.append((user_id, win_ratio, wins, total))
    
    # Sort by win ratio (and wins as tiebreaker)
    rankings.sort(key=lambda x: (x[1], x[2]), reverse=True)
    rankings = rankings[:limit]
    
    # Build entries
    entries = []
    user_rank = None
    
    for rank, (user_id, win_ratio, wins, total) in enumerate(rankings, 1):
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if user:
            entry = build_leaderboard_entry(
                user, rank, win_ratio, f"Win % ({wins}W/{total})", current_user.id
            )
            entries.append(entry)
            
            if user_id == current_user.id:
                user_rank = rank
    
    return LeaderboardResponse(
        leaderboard_type="pvp",
        time_range=TimeRange.ALL_TIME,
        entries=entries,
        user_rank=user_rank,
        total_participants=len(friend_ids),
        updated_at=datetime.now(timezone.utc),
    )
