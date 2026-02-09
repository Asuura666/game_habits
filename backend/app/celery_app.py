"""Celery application configuration."""

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "habit_tracker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.llm_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.stats_tasks",
        "app.tasks.cleanup_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_prefetch_multiplier=1,
    result_expires=3600,  # 1 hour
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Daily stats aggregation at midnight UTC
    "aggregate-daily-stats": {
        "task": "app.tasks.stats_tasks.aggregate_daily_stats",
        "schedule": 86400.0,  # 24 hours
    },
    # Reset weekly streak freeze every Monday at midnight UTC
    "reset-weekly-freeze": {
        "task": "app.tasks.cleanup_tasks.reset_weekly_freeze",
        "schedule": 604800.0,  # 7 days
    },
    # Clean old notifications (older than 30 days)
    "cleanup-notifications": {
        "task": "app.tasks.cleanup_tasks.cleanup_old_notifications",
        "schedule": 86400.0,  # 24 hours
    },
}
