"""
Celery tasks for LLM-powered task evaluation.
"""
import asyncio
from uuid import UUID

import structlog
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.models.task import Task
from app.models.user import User
from app.models.completion import Completion
from app.models.stats import DailyStats
from app.services.llm_service import get_llm_service
from app.tasks.notification_tasks import send_notification

logger = structlog.get_logger()


def run_async(coro):
    """Run an async coroutine in a sync context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _get_user_context(session: AsyncSession, user: User) -> dict:
    """
    Build user context for LLM evaluation.
    
    Args:
        session: Database session
        user: User model instance
        
    Returns:
        Dict with user stats and history
    """
    # Get completed tasks for similarity matching
    completed_tasks_query = (
        select(Task)
        .where(Task.user_id == user.id, Task.status == "completed")
        .order_by(Task.completed_at.desc())
        .limit(20)
    )
    result = await session.execute(completed_tasks_query)
    completed_tasks = result.scalars().all()
    
    # Get weekly task count
    from datetime import date, timedelta
    week_ago = date.today() - timedelta(days=7)
    weekly_tasks_query = (
        select(Task)
        .where(
            Task.user_id == user.id,
            Task.status == "completed",
            Task.completed_at >= week_ago,
        )
    )
    result = await session.execute(weekly_tasks_query)
    weekly_tasks = result.scalars().all()
    
    # Calculate category stats
    category_stats = {}
    for task in completed_tasks:
        cat = task.category or "general"
        if cat not in category_stats:
            category_stats[cat] = {
                "category": cat,
                "difficulties": [],
                "xp_values": [],
                "task_count": 0,
            }
        category_stats[cat]["task_count"] += 1
        if task.ai_difficulty:
            category_stats[cat]["difficulties"].append(task.ai_difficulty)
        if task.final_xp_reward:
            category_stats[cat]["xp_values"].append(task.final_xp_reward)
    
    # Calculate averages
    for cat, stats in category_stats.items():
        if stats["xp_values"]:
            stats["average_xp"] = sum(stats["xp_values"]) // len(stats["xp_values"])
        else:
            stats["average_xp"] = 50
        
        if stats["difficulties"]:
            # Most common difficulty
            from collections import Counter
            stats["average_difficulty"] = Counter(stats["difficulties"]).most_common(1)[0][0]
        else:
            stats["average_difficulty"] = "medium"
        
        # Clean up internal tracking
        del stats["difficulties"]
        del stats["xp_values"]
    
    # Build context
    return {
        "level": user.level,
        "total_xp": user.total_xp,
        "current_streak": user.current_streak,
        "best_streak": user.best_streak,
        "tasks_completed_total": len(completed_tasks),
        "tasks_completed_this_week": len(weekly_tasks),
        "average_completion_rate": 0.75,  # TODO: Calculate from DailyStats
        "preferred_difficulty": "medium",
        "completed_tasks": [
            {
                "title": t.title,
                "description": t.description,
                "difficulty": t.ai_difficulty,
                "xp_reward": t.final_xp_reward,
                "coins_reward": t.final_coins_reward,
                "category": t.category,
            }
            for t in completed_tasks[:10]
        ],
        "category_stats": category_stats,
    }


async def _evaluate_task_async(task_id: str, user_id: str) -> dict:
    """
    Async implementation of task evaluation.
    
    Args:
        task_id: UUID of the task to evaluate
        user_id: UUID of the task owner
        
    Returns:
        Dict with evaluation results
    """
    log = logger.bind(task_id=task_id, user_id=user_id)
    log.info("starting_task_evaluation")
    
    async with async_session_maker() as session:
        # Fetch task
        task_query = select(Task).where(Task.id == UUID(task_id))
        result = await session.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task:
            log.error("task_not_found")
            return {"error": "Task not found"}
        
        # Fetch user
        user_query = select(User).where(User.id == UUID(user_id))
        result = await session.execute(user_query)
        user = result.scalar_one_or_none()
        
        if not user:
            log.error("user_not_found")
            return {"error": "User not found"}
        
        # Build user context
        user_context = await _get_user_context(session, user)
        user_context["category"] = task.category
        user_context["priority"] = task.priority
        
        # Call LLM service
        llm_service = get_llm_service()
        evaluation = await llm_service.evaluate_task(
            title=task.title,
            description=task.description,
            user_context=user_context,
        )
        
        # Update task with evaluation
        task.ai_difficulty = evaluation.difficulty.value
        task.ai_xp_reward = evaluation.xp_reward
        task.ai_coins_reward = evaluation.coins_reward
        task.ai_reasoning = evaluation.reasoning
        task.ai_suggested_subtasks = evaluation.suggested_subtasks
        
        # Calculate final rewards
        task.calculate_final_rewards()
        
        await session.commit()
        
        log.info(
            "task_evaluation_complete",
            difficulty=evaluation.difficulty.value,
            xp_reward=evaluation.xp_reward,
        )
        
        return {
            "task_id": task_id,
            "difficulty": evaluation.difficulty.value,
            "xp_reward": evaluation.xp_reward,
            "coins_reward": evaluation.coins_reward,
            "reasoning": evaluation.reasoning,
            "suggested_subtasks": evaluation.suggested_subtasks,
            "estimated_time_minutes": evaluation.estimated_time_minutes,
        }


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
)
def evaluate_task_async(self, task_id: str, user_id: str):
    """
    Celery task to evaluate a task using LLM.
    
    Args:
        task_id: UUID string of the task
        user_id: UUID string of the task owner
        
    Returns:
        Evaluation result dict
    """
    log = logger.bind(
        task_id=task_id,
        user_id=user_id,
        celery_task_id=self.request.id,
        retry_count=self.request.retries,
    )
    
    try:
        log.info("evaluate_task_started")
        result = run_async(_evaluate_task_async(task_id, user_id))
        
        if "error" not in result:
            # Send notification to user
            send_notification.delay(
                user_id=user_id,
                type="task_evaluated",
                title="Task Evaluated! 🎯",
                message=f"Your task has been evaluated as {result['difficulty']} difficulty. "
                        f"Complete it to earn {result['xp_reward']} XP and {result['coins_reward']} coins!",
                data={
                    "task_id": task_id,
                    "difficulty": result["difficulty"],
                    "xp_reward": result["xp_reward"],
                    "coins_reward": result["coins_reward"],
                },
            )
        
        log.info("evaluate_task_completed", result=result)
        return result
        
    except MaxRetriesExceededError:
        log.error("evaluate_task_max_retries_exceeded")
        # Notify user of failure
        send_notification.delay(
            user_id=user_id,
            type="task_evaluation_failed",
            title="Evaluation Failed",
            message="We couldn't evaluate your task automatically. Default values have been applied.",
            data={"task_id": task_id},
        )
        raise
        
    except Exception as e:
        log.error("evaluate_task_failed", error=str(e), exc_info=True)
        raise


@shared_task(bind=True, max_retries=2)
def batch_evaluate_tasks(self, task_ids: list[str], user_id: str):
    """
    Evaluate multiple tasks in batch.
    
    Args:
        task_ids: List of task UUID strings
        user_id: UUID string of the task owner
    """
    log = logger.bind(user_id=user_id, task_count=len(task_ids))
    log.info("batch_evaluation_started")
    
    results = []
    for task_id in task_ids:
        try:
            result = evaluate_task_async.delay(task_id, user_id)
            results.append({"task_id": task_id, "celery_task_id": result.id})
        except Exception as e:
            log.error("batch_task_enqueue_failed", task_id=task_id, error=str(e))
            results.append({"task_id": task_id, "error": str(e)})
    
    log.info("batch_evaluation_enqueued", results=results)
    return results


# Aliases for backward compatibility with routers
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def evaluate_task_difficulty(self, task_id: str):
    """
    Evaluate task difficulty via LLM.
    Alias for evaluate_task_async that fetches user_id from task.
    
    Args:
        task_id: UUID string of the task to evaluate
    """
    log = logger.bind(task_id=task_id)
    
    async def get_user_id():
        async with async_session_maker() as session:
            task_query = select(Task).where(Task.id == UUID(task_id))
            result = await session.execute(task_query)
            task = result.scalar_one_or_none()
            if task:
                return str(task.user_id)
            return None
    
    user_id = run_async(get_user_id())
    
    if not user_id:
        log.error("task_not_found_for_evaluation")
        return {"error": "Task not found"}
    
    return run_async(_evaluate_task_async(task_id, user_id))


@shared_task(bind=True, max_retries=2)
def reevaluate_task(self, task_id: str):
    """
    Re-evaluate an existing task.
    Alias for evaluate_task_difficulty.
    
    Args:
        task_id: UUID string of the task to re-evaluate
    """
    return evaluate_task_difficulty.delay(task_id)
