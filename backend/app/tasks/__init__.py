"""
Celery tasks package.

This package contains all background tasks for the Habit Tracker application:
- llm_tasks: AI-powered task evaluation
- notification_tasks: User notification management
- stats_tasks: Daily statistics aggregation
- cleanup_tasks: Database cleanup and maintenance
"""

from app.tasks.llm_tasks import (
    evaluate_task_difficulty,
    reevaluate_task,
)
from app.tasks.notification_tasks import (
    send_notification,
    broadcast_notification,
    send_streak_warnings,
    mark_notifications_read,
)
from app.tasks.stats_tasks import (
    aggregate_daily_stats,
    calculate_leaderboard,
    recalculate_user_totals,
)
from app.tasks.cleanup_tasks import (
    reset_weekly_freeze,
    cleanup_old_notifications,
    reset_expired_rate_limits,
    cleanup_cancelled_tasks,
    purge_deleted_users,
    vacuum_analyze,
)

__all__ = [
    # LLM tasks
    "evaluate_task_difficulty",
    "reevaluate_task",
    # Notification tasks
    "send_notification",
    "broadcast_notification",
    "send_streak_warnings",
    "mark_notifications_read",
    # Stats tasks
    "aggregate_daily_stats",
    "calculate_leaderboard",
    "recalculate_user_totals",
    # Cleanup tasks
    "reset_weekly_freeze",
    "cleanup_old_notifications",
    "reset_expired_rate_limits",
    "cleanup_cancelled_tasks",
    "purge_deleted_users",
    "vacuum_analyze",
]
