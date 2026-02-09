"""
Celery tasks for notification management.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import structlog
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.models.notification import Notification
from app.models.user import User

logger = structlog.get_logger()


def run_async(coro):
    """Run an async coroutine in a sync context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _create_notification(
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    data: dict[str, Any] | None = None,
) -> dict:
    """
    Create a notification in the database.
    
    Args:
        user_id: UUID of the user
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        data: Optional additional data
        
    Returns:
        Created notification info
    """
    log = logger.bind(user_id=user_id, type=notification_type)
    
    async with async_session_maker() as session:
        # Verify user exists and has notifications enabled
        user_query = select(User).where(User.id == UUID(user_id))
        result = await session.execute(user_query)
        user = result.scalar_one_or_none()
        
        if not user:
            log.warning("notification_user_not_found")
            return {"error": "User not found"}
        
        if not user.notifications_enabled:
            log.debug("notifications_disabled_for_user")
            return {"skipped": True, "reason": "Notifications disabled"}
        
        # Create notification
        notification = Notification(
            user_id=UUID(user_id),
            type=notification_type,
            title=title,
            message=message,
            data=data or {},
        )
        
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        
        log.info("notification_created", notification_id=str(notification.id))
        
        return {
            "notification_id": str(notification.id),
            "user_id": user_id,
            "type": notification_type,
            "title": title,
        }


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_notification(
    self,
    user_id: str,
    type: str,
    title: str,
    message: str,
    data: dict[str, Any] | None = None,
):
    """
    Create a notification for a user.
    
    Args:
        user_id: UUID string of the user
        type: Notification type (friend_request, badge_unlocked, etc.)
        title: Notification title
        message: Notification message
        data: Optional additional data
        
    Returns:
        Created notification info
    """
    log = logger.bind(
        user_id=user_id,
        type=type,
        celery_task_id=self.request.id,
    )
    
    try:
        log.info("send_notification_started")
        result = run_async(_create_notification(user_id, type, title, message, data))
        log.info("send_notification_completed", result=result)
        return result
        
    except Exception as e:
        log.error("send_notification_failed", error=str(e), exc_info=True)
        raise self.retry(exc=e)


async def _broadcast_notification(
    user_ids: list[str],
    notification_type: str,
    title: str,
    message: str,
    data: dict[str, Any] | None = None,
) -> dict:
    """
    Broadcast a notification to multiple users.
    
    Args:
        user_ids: List of user UUIDs
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        data: Optional additional data
        
    Returns:
        Broadcast results
    """
    log = logger.bind(user_count=len(user_ids), type=notification_type)
    log.info("broadcast_started")
    
    async with async_session_maker() as session:
        # Get users with notifications enabled
        users_query = (
            select(User)
            .where(
                User.id.in_([UUID(uid) for uid in user_ids]),
                User.notifications_enabled == True,
            )
        )
        result = await session.execute(users_query)
        users = result.scalars().all()
        
        # Create notifications
        notifications = []
        for user in users:
            notification = Notification(
                user_id=user.id,
                type=notification_type,
                title=title,
                message=message,
                data=data or {},
            )
            notifications.append(notification)
        
        session.add_all(notifications)
        await session.commit()
        
        log.info(
            "broadcast_completed",
            sent_count=len(notifications),
            skipped_count=len(user_ids) - len(notifications),
        )
        
        return {
            "sent_count": len(notifications),
            "skipped_count": len(user_ids) - len(notifications),
            "type": notification_type,
        }


@shared_task(bind=True, max_retries=2)
def broadcast_notification(
    self,
    user_ids: list[str],
    type: str,
    title: str,
    message: str,
    data: dict[str, Any] | None = None,
):
    """
    Broadcast a notification to multiple users.
    
    Args:
        user_ids: List of user UUID strings
        type: Notification type
        title: Notification title
        message: Notification message
        data: Optional additional data
        
    Returns:
        Broadcast results
    """
    log = logger.bind(
        user_count=len(user_ids),
        type=type,
        celery_task_id=self.request.id,
    )
    
    try:
        log.info("broadcast_notification_started")
        result = run_async(_broadcast_notification(user_ids, type, title, message, data))
        log.info("broadcast_notification_completed", result=result)
        return result
        
    except Exception as e:
        log.error("broadcast_notification_failed", error=str(e), exc_info=True)
        raise self.retry(exc=e)


async def _send_streak_warnings() -> dict:
    """
    Send streak warning notifications to users at risk.
    
    Returns:
        Count of warnings sent
    """
    from datetime import date
    
    log = logger.bind(task="streak_warnings")
    log.info("checking_streak_warnings")
    
    async with async_session_maker() as session:
        # Find users who haven't completed anything today
        # and have an active streak
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        users_query = (
            select(User)
            .where(
                User.current_streak > 0,
                User.last_activity_date < today,
                User.notifications_enabled == True,
            )
        )
        result = await session.execute(users_query)
        at_risk_users = result.scalars().all()
        
        # Create warning notifications
        notifications = []
        for user in at_risk_users:
            notification = Notification(
                user_id=user.id,
                type="streak_warning",
                title="🔥 Streak at Risk!",
                message=f"Complete a habit today to keep your {user.current_streak}-day streak alive!",
                data={
                    "current_streak": user.current_streak,
                    "streak_freeze_available": user.streak_freeze_available,
                },
            )
            notifications.append(notification)
        
        if notifications:
            session.add_all(notifications)
            await session.commit()
        
        log.info("streak_warnings_sent", count=len(notifications))
        
        return {"warnings_sent": len(notifications)}


@shared_task
def send_streak_warnings():
    """
    Send streak warning notifications to users who haven't completed
    anything today and have an active streak.
    """
    log = logger.bind(task="streak_warnings")
    
    try:
        log.info("send_streak_warnings_started")
        result = run_async(_send_streak_warnings())
        log.info("send_streak_warnings_completed", result=result)
        return result
        
    except Exception as e:
        log.error("send_streak_warnings_failed", error=str(e), exc_info=True)
        raise


async def _mark_notifications_read(user_id: str, notification_ids: list[str]) -> dict:
    """
    Mark multiple notifications as read.
    
    Args:
        user_id: User UUID
        notification_ids: List of notification UUIDs to mark as read
        
    Returns:
        Count of updated notifications
    """
    from sqlalchemy import update
    
    async with async_session_maker() as session:
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == UUID(user_id),
                Notification.id.in_([UUID(nid) for nid in notification_ids]),
            )
            .values(is_read=True)
        )
        result = await session.execute(stmt)
        await session.commit()
        
        return {"marked_read": result.rowcount}


@shared_task
def mark_notifications_read(user_id: str, notification_ids: list[str]):
    """
    Mark notifications as read in bulk.
    
    Args:
        user_id: User UUID string
        notification_ids: List of notification UUID strings
    """
    log = logger.bind(user_id=user_id, count=len(notification_ids))
    
    try:
        log.info("mark_notifications_read_started")
        result = run_async(_mark_notifications_read(user_id, notification_ids))
        log.info("mark_notifications_read_completed", result=result)
        return result
        
    except Exception as e:
        log.error("mark_notifications_read_failed", error=str(e), exc_info=True)
        raise
