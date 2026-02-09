"""
Celery tasks for statistics aggregation.
"""
import asyncio
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

import structlog
from celery import shared_task
from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.models.completion import Completion
from app.models.habit import Habit
from app.models.stats import DailyStats
from app.models.task import Task
from app.models.transaction import CoinTransaction, XPTransaction
from app.models.user import User

logger = structlog.get_logger()


def run_async(coro):
    """Run an async coroutine in a sync context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _aggregate_user_daily_stats(
    session: AsyncSession,
    user_id: UUID,
    target_date: date,
) -> DailyStats | None:
    """
    Aggregate daily stats for a single user.
    
    Args:
        session: Database session
        user_id: User UUID
        target_date: Date to aggregate stats for
        
    Returns:
        Created or updated DailyStats
    """
    log = logger.bind(user_id=str(user_id), date=str(target_date))
    
    # Count total habits for the day
    habits_query = (
        select(func.count(Habit.id))
        .where(
            Habit.user_id == user_id,
            Habit.is_active == True,
        )
    )
    result = await session.execute(habits_query)
    habits_total = result.scalar() or 0
    
    # Count completed habits for the day
    completions_query = (
        select(func.count(Completion.id))
        .where(
            Completion.user_id == user_id,
            func.date(Completion.completed_at) == target_date,
        )
    )
    result = await session.execute(completions_query)
    habits_completed = result.scalar() or 0
    
    # Count completed tasks for the day
    tasks_query = (
        select(func.count(Task.id))
        .where(
            Task.user_id == user_id,
            Task.status == "completed",
            func.date(Task.completed_at) == target_date,
        )
    )
    result = await session.execute(tasks_query)
    tasks_completed = result.scalar() or 0
    
    # Sum XP earned for the day
    xp_query = (
        select(func.coalesce(func.sum(XPTransaction.amount), 0))
        .where(
            XPTransaction.user_id == user_id,
            func.date(XPTransaction.created_at) == target_date,
            XPTransaction.amount > 0,
        )
    )
    result = await session.execute(xp_query)
    xp_earned = result.scalar() or 0
    
    # Sum coins earned for the day
    coins_earned_query = (
        select(func.coalesce(func.sum(CoinTransaction.amount), 0))
        .where(
            CoinTransaction.user_id == user_id,
            func.date(CoinTransaction.created_at) == target_date,
            CoinTransaction.amount > 0,
        )
    )
    result = await session.execute(coins_earned_query)
    coins_earned = result.scalar() or 0
    
    # Sum coins spent for the day
    coins_spent_query = (
        select(func.coalesce(func.abs(func.sum(CoinTransaction.amount)), 0))
        .where(
            CoinTransaction.user_id == user_id,
            func.date(CoinTransaction.created_at) == target_date,
            CoinTransaction.amount < 0,
        )
    )
    result = await session.execute(coins_spent_query)
    coins_spent = result.scalar() or 0
    
    # Calculate completion rate
    completion_rate = Decimal("0")
    if habits_total > 0:
        completion_rate = Decimal(
            (habits_completed / habits_total) * 100
        ).quantize(Decimal("0.01"))
    
    # Upsert daily stats
    stmt = insert(DailyStats).values(
        user_id=user_id,
        date=target_date,
        habits_total=habits_total,
        habits_completed=habits_completed,
        completion_rate=completion_rate,
        tasks_completed=tasks_completed,
        xp_earned=xp_earned,
        coins_earned=coins_earned,
        coins_spent=coins_spent,
        combats_won=0,  # TODO: Aggregate from combat results
        combats_lost=0,
    )
    
    # On conflict, update
    stmt = stmt.on_conflict_do_update(
        constraint="uq_daily_stats_user_date",
        set_={
            "habits_total": stmt.excluded.habits_total,
            "habits_completed": stmt.excluded.habits_completed,
            "completion_rate": stmt.excluded.completion_rate,
            "tasks_completed": stmt.excluded.tasks_completed,
            "xp_earned": stmt.excluded.xp_earned,
            "coins_earned": stmt.excluded.coins_earned,
            "coins_spent": stmt.excluded.coins_spent,
        },
    )
    
    await session.execute(stmt)
    
    log.debug(
        "user_stats_aggregated",
        habits_completed=habits_completed,
        habits_total=habits_total,
        completion_rate=float(completion_rate),
    )
    
    return None


async def _aggregate_daily_stats_async(target_date: date | None = None) -> dict:
    """
    Aggregate daily stats for all users.
    
    Args:
        target_date: Date to aggregate (defaults to yesterday)
        
    Returns:
        Aggregation results
    """
    if target_date is None:
        target_date = date.today() - timedelta(days=1)
    
    log = logger.bind(target_date=str(target_date))
    log.info("aggregation_started")
    
    async with async_session_maker() as session:
        # Get all active users
        users_query = select(User.id).where(User.deleted_at.is_(None))
        result = await session.execute(users_query)
        user_ids = [row[0] for row in result.fetchall()]
        
        log.info("processing_users", user_count=len(user_ids))
        
        # Aggregate stats for each user
        success_count = 0
        error_count = 0
        
        for user_id in user_ids:
            try:
                await _aggregate_user_daily_stats(session, user_id, target_date)
                success_count += 1
            except Exception as e:
                error_count += 1
                log.error(
                    "user_aggregation_failed",
                    user_id=str(user_id),
                    error=str(e),
                )
        
        await session.commit()
        
        log.info(
            "aggregation_completed",
            success_count=success_count,
            error_count=error_count,
        )
        
        return {
            "date": str(target_date),
            "users_processed": success_count,
            "errors": error_count,
        }


@shared_task
def aggregate_daily_stats(target_date: str | None = None):
    """
    Aggregate daily stats for all users.
    
    Should run once per day (configured in celery beat schedule).
    Aggregates stats from the previous day by default.
    
    Args:
        target_date: Optional date string (YYYY-MM-DD) to aggregate
    """
    log = logger.bind(task="aggregate_daily_stats")
    
    try:
        parsed_date = None
        if target_date:
            parsed_date = date.fromisoformat(target_date)
        
        log.info("aggregate_daily_stats_started", date=target_date)
        result = run_async(_aggregate_daily_stats_async(parsed_date))
        log.info("aggregate_daily_stats_completed", result=result)
        return result
        
    except Exception as e:
        log.error("aggregate_daily_stats_failed", error=str(e), exc_info=True)
        raise


async def _calculate_leaderboard_positions() -> dict:
    """
    Calculate and cache leaderboard positions.
    
    Returns:
        Leaderboard update results
    """
    log = logger.bind(task="leaderboard")
    log.info("calculating_leaderboard")
    
    async with async_session_maker() as session:
        # Get weekly XP for all public users
        week_start = date.today() - timedelta(days=date.today().weekday())
        
        leaderboard_query = (
            select(
                User.id,
                User.username,
                func.coalesce(func.sum(DailyStats.xp_earned), 0).label("weekly_xp"),
            )
            .outerjoin(
                DailyStats,
                and_(
                    DailyStats.user_id == User.id,
                    DailyStats.date >= week_start,
                ),
            )
            .where(
                User.is_public == True,
                User.deleted_at.is_(None),
            )
            .group_by(User.id, User.username)
            .order_by(func.sum(DailyStats.xp_earned).desc().nullslast())
            .limit(100)
        )
        
        result = await session.execute(leaderboard_query)
        leaderboard = result.fetchall()
        
        log.info("leaderboard_calculated", entries=len(leaderboard))
        
        return {
            "week_start": str(week_start),
            "entries": len(leaderboard),
            "top_3": [
                {"username": row.username, "xp": row.weekly_xp}
                for row in leaderboard[:3]
            ],
        }


@shared_task
def calculate_leaderboard():
    """
    Calculate and update leaderboard positions.
    
    Can be called periodically to refresh cached leaderboard data.
    """
    log = logger.bind(task="calculate_leaderboard")
    
    try:
        log.info("calculate_leaderboard_started")
        result = run_async(_calculate_leaderboard_positions())
        log.info("calculate_leaderboard_completed", result=result)
        return result
        
    except Exception as e:
        log.error("calculate_leaderboard_failed", error=str(e), exc_info=True)
        raise


async def _recalculate_user_totals(user_id: str) -> dict:
    """
    Recalculate user's total XP and coins from transactions.
    
    Used for consistency checks and corrections.
    
    Args:
        user_id: User UUID string
        
    Returns:
        Updated totals
    """
    log = logger.bind(user_id=user_id)
    log.info("recalculating_user_totals")
    
    async with async_session_maker() as session:
        uid = UUID(user_id)
        
        # Sum all XP transactions
        xp_query = (
            select(func.coalesce(func.sum(XPTransaction.amount), 0))
            .where(XPTransaction.user_id == uid)
        )
        result = await session.execute(xp_query)
        total_xp = result.scalar() or 0
        
        # Sum all coin transactions
        coins_query = (
            select(func.coalesce(func.sum(CoinTransaction.amount), 0))
            .where(CoinTransaction.user_id == uid)
        )
        result = await session.execute(coins_query)
        total_coins = result.scalar() or 0
        
        # Update user
        user_query = select(User).where(User.id == uid)
        result = await session.execute(user_query)
        user = result.scalar_one_or_none()
        
        if user:
            old_xp = user.total_xp
            old_coins = user.coins
            
            user.total_xp = max(0, total_xp)
            user.coins = max(0, total_coins)
            
            await session.commit()
            
            log.info(
                "user_totals_recalculated",
                old_xp=old_xp,
                new_xp=user.total_xp,
                old_coins=old_coins,
                new_coins=user.coins,
            )
            
            return {
                "user_id": user_id,
                "old_xp": old_xp,
                "new_xp": user.total_xp,
                "old_coins": old_coins,
                "new_coins": user.coins,
            }
        
        return {"error": "User not found"}


@shared_task
def recalculate_user_totals(user_id: str):
    """
    Recalculate a user's total XP and coins.
    
    Args:
        user_id: User UUID string
    """
    log = logger.bind(user_id=user_id)
    
    try:
        log.info("recalculate_user_totals_started")
        result = run_async(_recalculate_user_totals(user_id))
        log.info("recalculate_user_totals_completed", result=result)
        return result
        
    except Exception as e:
        log.error("recalculate_user_totals_failed", error=str(e), exc_info=True)
        raise
