"""
Celery tasks for cleanup and maintenance.
"""
# import asyncio  # Removed - using celery_utils
from datetime import datetime, timedelta
from uuid import UUID

import structlog
from celery import shared_task
from sqlalchemy import delete, update, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.tasks.celery_utils import get_celery_db_session, run_async
from app.models.notification import Notification
from app.models.user import User
from app.models.stats import RateLimit

logger = structlog.get_logger()



async def _reset_weekly_freeze_async() -> dict:
    """
    Reset streak freeze availability for all users.
    
    Each user gets 1 streak freeze per week.
    Should run every Monday at midnight UTC.
    
    Returns:
        Count of users updated
    """
    log = logger.bind(task="reset_weekly_freeze")
    log.info("resetting_weekly_freeze")
    
    async with get_celery_db_session() as session:
        # Reset streak_freeze_available to 1 for all users
        stmt = (
            update(User)
            .where(User.deleted_at.is_(None))
            .values(streak_freeze_available=1)
        )
        result = await session.execute(stmt)
        await session.commit()
        
        updated_count = result.rowcount
        log.info("weekly_freeze_reset_complete", users_updated=updated_count)
        
        return {
            "users_updated": updated_count,
            "reset_at": datetime.utcnow().isoformat(),
        }


@shared_task
def reset_weekly_freeze():
    """
    Reset weekly streak freeze for all users.
    
    Scheduled to run every Monday at midnight UTC via celery beat.
    Resets streak_freeze_available to 1 for all active users.
    """
    log = logger.bind(task="reset_weekly_freeze")
    
    try:
        log.info("reset_weekly_freeze_started")
        result = run_async(_reset_weekly_freeze_async())
        log.info("reset_weekly_freeze_completed", result=result)
        return result
        
    except Exception as e:
        log.error("reset_weekly_freeze_failed", error=str(e), exc_info=True)
        raise


async def _cleanup_old_notifications_async(days: int = 30) -> dict:
    """
    Delete notifications older than specified days.
    
    Args:
        days: Number of days to keep notifications
        
    Returns:
        Count of deleted notifications
    """
    log = logger.bind(task="cleanup_notifications", retention_days=days)
    log.info("cleaning_old_notifications")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    async with get_celery_db_session() as session:
        # Delete old read notifications (keep unread a bit longer)
        stmt = delete(Notification).where(
            Notification.created_at < cutoff_date,
            Notification.is_read == True,
        )
        result = await session.execute(stmt)
        read_deleted = result.rowcount
        
        # Delete very old unread notifications (45 days)
        very_old_cutoff = datetime.utcnow() - timedelta(days=days + 15)
        stmt = delete(Notification).where(
            Notification.created_at < very_old_cutoff,
        )
        result = await session.execute(stmt)
        unread_deleted = result.rowcount
        
        await session.commit()
        
        total_deleted = read_deleted + unread_deleted
        log.info(
            "notifications_cleanup_complete",
            read_deleted=read_deleted,
            unread_deleted=unread_deleted,
            total=total_deleted,
        )
        
        return {
            "read_deleted": read_deleted,
            "unread_deleted": unread_deleted,
            "total_deleted": total_deleted,
            "cutoff_date": cutoff_date.isoformat(),
        }


@shared_task
def cleanup_old_notifications(days: int = 30):
    """
    Delete old notifications to keep the database clean.
    
    Scheduled to run daily via celery beat.
    
    Args:
        days: Number of days to keep read notifications (default 30)
    """
    log = logger.bind(task="cleanup_old_notifications")
    
    try:
        log.info("cleanup_old_notifications_started", days=days)
        result = run_async(_cleanup_old_notifications_async(days))
        log.info("cleanup_old_notifications_completed", result=result)
        return result
        
    except Exception as e:
        log.error("cleanup_old_notifications_failed", error=str(e), exc_info=True)
        raise


async def _reset_expired_rate_limits_async() -> dict:
    """
    Reset expired rate limits.
    
    Returns:
        Count of rate limits reset
    """
    log = logger.bind(task="reset_rate_limits")
    log.info("resetting_expired_rate_limits")
    
    now = datetime.utcnow()
    
    async with get_celery_db_session() as session:
        # Reset expired rate limits
        stmt = (
            update(RateLimit)
            .where(RateLimit.reset_at <= now)
            .values(
                current_count=0,
                reset_at=now + timedelta(days=1),
            )
        )
        result = await session.execute(stmt)
        await session.commit()
        
        reset_count = result.rowcount
        log.info("rate_limits_reset_complete", count=reset_count)
        
        return {
            "rate_limits_reset": reset_count,
            "reset_at": now.isoformat(),
        }


@shared_task
def reset_expired_rate_limits():
    """
    Reset rate limits that have expired.
    
    Can be scheduled hourly to clean up expired rate limits.
    """
    log = logger.bind(task="reset_expired_rate_limits")
    
    try:
        log.info("reset_expired_rate_limits_started")
        result = run_async(_reset_expired_rate_limits_async())
        log.info("reset_expired_rate_limits_completed", result=result)
        return result
        
    except Exception as e:
        log.error("reset_expired_rate_limits_failed", error=str(e), exc_info=True)
        raise


async def _cleanup_cancelled_tasks_async(days: int = 7) -> dict:
    """
    Delete cancelled tasks older than specified days.
    
    Args:
        days: Number of days to keep cancelled tasks
        
    Returns:
        Count of deleted tasks
    """
    from app.models.task import Task
    
    log = logger.bind(task="cleanup_cancelled_tasks", days=days)
    log.info("cleaning_cancelled_tasks")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    async with get_celery_db_session() as session:
        stmt = delete(Task).where(
            Task.status == "cancelled",
            Task.updated_at < cutoff_date,
        )
        result = await session.execute(stmt)
        await session.commit()
        
        deleted_count = result.rowcount
        log.info("cancelled_tasks_cleanup_complete", deleted=deleted_count)
        
        return {
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
        }


@shared_task
def cleanup_cancelled_tasks(days: int = 7):
    """
    Delete old cancelled tasks.
    
    Args:
        days: Number of days to keep cancelled tasks (default 7)
    """
    log = logger.bind(task="cleanup_cancelled_tasks")
    
    try:
        log.info("cleanup_cancelled_tasks_started", days=days)
        result = run_async(_cleanup_cancelled_tasks_async(days))
        log.info("cleanup_cancelled_tasks_completed", result=result)
        return result
        
    except Exception as e:
        log.error("cleanup_cancelled_tasks_failed", error=str(e), exc_info=True)
        raise


async def _purge_deleted_users_async(days: int = 30) -> dict:
    """
    Permanently delete soft-deleted users after grace period.
    
    Args:
        days: Number of days after soft-delete to permanently remove
        
    Returns:
        Count of permanently deleted users
    """
    log = logger.bind(task="purge_deleted_users", days=days)
    log.info("purging_deleted_users")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    async with get_celery_db_session() as session:
        # Count users to be deleted
        count_query = (
            select(func.count(User.id))
            .where(
                User.deleted_at.isnot(None),
                User.deleted_at < cutoff_date,
            )
        )
        result = await session.execute(count_query)
        user_count = result.scalar() or 0
        
        if user_count > 0:
            # Delete users (cascades to related data)
            stmt = delete(User).where(
                User.deleted_at.isnot(None),
                User.deleted_at < cutoff_date,
            )
            await session.execute(stmt)
            await session.commit()
        
        log.info("deleted_users_purged", count=user_count)
        
        return {
            "users_purged": user_count,
            "cutoff_date": cutoff_date.isoformat(),
        }


@shared_task
def purge_deleted_users(days: int = 30):
    """
    Permanently delete users who were soft-deleted more than X days ago.
    
    This gives users a grace period to recover their account.
    
    Args:
        days: Grace period in days (default 30)
    """
    log = logger.bind(task="purge_deleted_users")
    
    try:
        log.info("purge_deleted_users_started", days=days)
        result = run_async(_purge_deleted_users_async(days))
        log.info("purge_deleted_users_completed", result=result)
        return result
        
    except Exception as e:
        log.error("purge_deleted_users_failed", error=str(e), exc_info=True)
        raise


async def _vacuum_analyze_async() -> dict:
    """
    Run VACUUM ANALYZE on high-churn tables.
    
    Returns:
        Tables vacuumed
    """
    from sqlalchemy import text
    
    log = logger.bind(task="vacuum_analyze")
    log.info("running_vacuum_analyze")
    
    tables = [
        "notifications",
        "completions",
        "daily_stats",
        "xp_transactions",
        "coin_transactions",
    ]
    
    async with get_celery_db_session() as session:
        for table in tables:
            try:
                # Note: VACUUM cannot run in a transaction
                # This is a simplified version - in production you'd use
                # a separate connection without transaction
                await session.execute(text(f"ANALYZE {table}"))
                log.debug("table_analyzed", table=table)
            except Exception as e:
                log.warning("analyze_failed", table=table, error=str(e))
        
        await session.commit()
    
    log.info("vacuum_analyze_complete", tables=tables)
    
    return {
        "tables_analyzed": tables,
        "completed_at": datetime.utcnow().isoformat(),
    }


@shared_task
def vacuum_analyze():
    """
    Run ANALYZE on high-churn tables to update statistics.
    
    Should be scheduled to run weekly during low-traffic periods.
    """
    log = logger.bind(task="vacuum_analyze")
    
    try:
        log.info("vacuum_analyze_started")
        result = run_async(_vacuum_analyze_async())
        log.info("vacuum_analyze_completed", result=result)
        return result
        
    except Exception as e:
        log.error("vacuum_analyze_failed", error=str(e), exc_info=True)
        raise
