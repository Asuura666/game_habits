"""
Tasks Router

Endpoints for managing one-time tasks with AI evaluation:
- CRUD operations for tasks
- AI-powered difficulty evaluation via Celery
- Task completion with XP/coin rewards
"""

from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.subtask import Subtask
from app.models.task import Task
from app.schemas.task import (
    Difficulty,
    Priority,
    SubtaskCreate,
    SubtaskResponse,
    TaskCreate,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
    TaskWithEvaluation,
    TaskEvaluation,
)
from app.services.xp_service import calculate_task_xp, add_xp
from app.services.streak_service import get_streak_multiplier
from app.tasks.llm_tasks import evaluate_task_difficulty, reevaluate_task
from app.utils.dependencies import CurrentUser

logger = structlog.get_logger()
router = APIRouter(prefix="/tasks", tags=["Tasks"])


# Map schema enums to model string values
PRIORITY_MAP = {
    Priority.LOW: "low",
    Priority.MEDIUM: "medium",
    Priority.HIGH: "high",
    Priority.URGENT: "urgent",
}

DIFFICULTY_MAP = {
    Difficulty.TRIVIAL: "trivial",
    Difficulty.EASY: "easy",
    Difficulty.MEDIUM: "medium",
    Difficulty.HARD: "hard",
    Difficulty.EPIC: "epic",
    Difficulty.LEGENDARY: "legendary",
}

STATUS_MAP = {
    TaskStatus.PENDING: "pending",
    TaskStatus.IN_PROGRESS: "in_progress",
    TaskStatus.COMPLETED: "completed",
    TaskStatus.CANCELLED: "cancelled",
}


def task_to_response(task: Task) -> TaskResponse:
    """Convert Task model to TaskResponse schema."""
    subtask_responses = [
        SubtaskResponse(
            id=s.id,
            title=s.title,
            is_completed=s.is_completed,
            completed_at=s.completed_at,
        )
        for s in (task.subtasks or [])
    ]
    
    completed_subtasks = sum(1 for s in (task.subtasks or []) if s.is_completed)
    
    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        difficulty=task.ai_difficulty or "medium",
        due_date=datetime.combine(task.due_date, task.due_time or datetime.min.time()) if task.due_date else None,
        tags=[],  # Tags would need to be stored separately
        xp_reward=task.final_xp_reward or task.ai_xp_reward or 30,
        coins_reward=task.final_coins_reward or task.ai_coins_reward or 15,
        status=task.status,
        subtasks=subtask_responses,
        subtasks_completed=completed_subtasks,
        subtasks_total=len(task.subtasks or []),
        ai_reasoning=task.ai_reasoning,
        estimated_time_minutes=None,  # Could be stored in ai_suggested_subtasks JSON
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
    )


@router.get(
    "/",
    response_model=list[TaskResponse],
    summary="List my tasks",
    description="Get all tasks for the authenticated user",
)
async def list_tasks(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status (pending, in_progress, completed, cancelled)"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    include_completed: bool = Query(False, description="Include completed tasks"),
) -> list[TaskResponse]:
    """List all tasks for the current user."""
    query = select(Task).where(Task.user_id == current_user.id)
    
    if status:
        query = query.where(Task.status == status)
    elif not include_completed:
        query = query.where(Task.status.in_(["pending", "in_progress"]))
    
    if priority:
        query = query.where(Task.priority == priority)
    
    # Order by priority (urgent first), then due date
    query = query.order_by(
        # Urgent tasks first
        Task.priority.desc(),
        # Then by due date (null last)
        Task.due_date.asc().nulls_last(),
        Task.created_at.desc(),
    )
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return [task_to_response(task) for task in tasks]


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Create a new task. If use_ai_evaluation is True, triggers async LLM evaluation via Celery.",
)
async def create_task(
    task_data: TaskCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Create a new task with optional AI evaluation."""
    # Create task
    task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        priority=PRIORITY_MAP.get(task_data.priority, "medium"),
        due_date=task_data.due_date.date() if task_data.due_date else None,
        due_time=task_data.due_date.time() if task_data.due_date else None,
    )
    
    # If manual difficulty/rewards provided, use them
    if task_data.difficulty:
        task.ai_difficulty = DIFFICULTY_MAP.get(task_data.difficulty, "medium")
    if task_data.xp_reward:
        task.ai_xp_reward = task_data.xp_reward
        task.final_xp_reward = task_data.xp_reward
    if task_data.coins_reward:
        task.ai_coins_reward = task_data.coins_reward
        task.final_coins_reward = task_data.coins_reward
    
    db.add(task)
    await db.flush()  # Get task ID before creating subtasks
    
    # Create subtasks if provided
    if task_data.subtasks:
        for subtask_data in task_data.subtasks:
            subtask = Subtask(
                task_id=task.id,
                title=subtask_data.title,
                is_completed=subtask_data.is_completed,
            )
            db.add(subtask)
    
    await db.commit()
    await db.refresh(task)
    
    logger.info(
        "Task created",
        task_id=str(task.id),
        user_id=str(current_user.id),
        title=task.title,
        use_ai=task_data.use_ai_evaluation,
    )
    
    # Trigger AI evaluation if requested and no manual values
    if task_data.use_ai_evaluation and not task_data.difficulty:
        evaluate_task_difficulty.delay(str(task.id))
        logger.info("AI evaluation triggered", task_id=str(task.id))
    
    return task_to_response(task)


@router.get(
    "/today",
    response_model=list[TaskResponse],
    summary="Today's tasks",
    description="Get tasks due today",
)
async def get_today_tasks(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[TaskResponse]:
    """Get tasks due today."""
    today = date.today()
    
    result = await db.execute(
        select(Task)
        .where(
            and_(
                Task.user_id == current_user.id,
                Task.due_date == today,
                Task.status.in_(["pending", "in_progress"]),
            )
        )
        .order_by(Task.priority.desc(), Task.due_time.asc().nulls_last())
    )
    tasks = result.scalars().all()
    
    return [task_to_response(task) for task in tasks]


@router.get(
    "/overdue",
    response_model=list[TaskResponse],
    summary="Overdue tasks",
    description="Get tasks that are past their due date",
)
async def get_overdue_tasks(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[TaskResponse]:
    """Get overdue tasks."""
    today = date.today()
    
    result = await db.execute(
        select(Task)
        .where(
            and_(
                Task.user_id == current_user.id,
                Task.due_date < today,
                Task.status.in_(["pending", "in_progress"]),
            )
        )
        .order_by(Task.due_date.asc(), Task.priority.desc())
    )
    tasks = result.scalars().all()
    
    return [task_to_response(task) for task in tasks]


@router.get(
    "/{task_id}",
    response_model=TaskWithEvaluation,
    summary="Get task details",
    description="Get details of a specific task including AI evaluation",
)
async def get_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TaskWithEvaluation:
    """Get a specific task by ID with full evaluation details."""
    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.user_id == current_user.id,
            )
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Build base response
    base = task_to_response(task)
    
    # Add evaluation if available
    evaluation = None
    if task.ai_difficulty and task.ai_reasoning:
        evaluation = TaskEvaluation(
            difficulty=task.ai_difficulty,
            xp_reward=task.ai_xp_reward or 30,
            coins_reward=task.ai_coins_reward or 15,
            reasoning=task.ai_reasoning,
            suggested_subtasks=task.ai_suggested_subtasks or [],
            estimated_time_minutes=60,  # Default
        )
    
    return TaskWithEvaluation(
        **base.model_dump(),
        evaluation=evaluation,
    )


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update task",
    description="Update an existing task",
)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Update an existing task."""
    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.user_id == current_user.id,
            )
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)
    
    if "title" in update_data:
        task.title = update_data["title"]
    if "description" in update_data:
        task.description = update_data["description"]
    if "priority" in update_data and update_data["priority"]:
        task.priority = PRIORITY_MAP.get(update_data["priority"], task.priority)
    if "difficulty" in update_data and update_data["difficulty"]:
        task.ai_difficulty = DIFFICULTY_MAP.get(update_data["difficulty"], task.ai_difficulty)
    if "due_date" in update_data:
        if update_data["due_date"]:
            task.due_date = update_data["due_date"].date()
            task.due_time = update_data["due_date"].time()
        else:
            task.due_date = None
            task.due_time = None
    if "status" in update_data and update_data["status"]:
        task.status = STATUS_MAP.get(update_data["status"], task.status)
        if task.status == "completed":
            task.completed_at = datetime.now(timezone.utc)
    
    task.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    
    logger.info(
        "Task updated",
        task_id=str(task.id),
        user_id=str(current_user.id),
    )
    
    return task_to_response(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Permanently delete a task",
)
async def delete_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a task permanently."""
    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.user_id == current_user.id,
            )
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    await db.delete(task)
    await db.commit()
    
    logger.info(
        "Task deleted",
        task_id=str(task_id),
        user_id=str(current_user.id),
    )


@router.post(
    "/{task_id}/complete",
    response_model=TaskWithEvaluation,
    summary="Complete task",
    description="Mark a task as completed and receive XP/coins reward",
)
async def complete_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TaskWithEvaluation:
    """Complete a task and receive rewards."""
    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.user_id == current_user.id,
            )
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    if task.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is already completed",
        )
    
    if task.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot complete a cancelled task",
        )
    
    # Mark as completed
    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc)
    task.updated_at = datetime.now(timezone.utc)
    
    # Check if completed before due date
    completed_early = False
    if task.due_date and task.due_date > date.today():
        completed_early = True
    
    # Calculate XP using the new service
    xp_earned = calculate_task_xp(task, completed_early=completed_early)
    coins_earned = int(xp_earned * 0.5)  # Coins = 50% of XP
    
    # Add XP to user (this handles level up checks)
    add_xp(
        db=db,  # type: ignore - async session compatibility
        user=current_user,
        amount=xp_earned,
        source_type="task",
        source_id=task.id,
        description=f"Completed task: {task.title}",
    )
    
    # Add coins
    current_user.coins += coins_earned
    
    await db.commit()
    await db.refresh(task)
    
    logger.info(
        "Task completed",
        task_id=str(task.id),
        user_id=str(current_user.id),
        xp_earned=xp_earned,
        coins_earned=coins_earned,
    )
    
    # Build response
    base = task_to_response(task)
    
    evaluation = None
    if task.ai_difficulty:
        evaluation = TaskEvaluation(
            difficulty=task.ai_difficulty,
            xp_reward=task.ai_xp_reward or 30,
            coins_reward=task.ai_coins_reward or 15,
            reasoning=task.ai_reasoning or "Task completed",
            suggested_subtasks=task.ai_suggested_subtasks or [],
            estimated_time_minutes=60,
        )
    
    return TaskWithEvaluation(
        **base.model_dump(),
        evaluation=evaluation,
    )


@router.post(
    "/{task_id}/reevaluate",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Re-evaluate task",
    description="Trigger AI re-evaluation of task difficulty and rewards",
)
async def reevaluate_task_endpoint(
    task_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Trigger AI re-evaluation of a task."""
    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.user_id == current_user.id,
            )
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    if task.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot re-evaluate a completed or cancelled task",
        )
    
    # Trigger async re-evaluation
    reevaluate_task.delay(str(task.id))
    
    logger.info(
        "Task re-evaluation triggered",
        task_id=str(task.id),
        user_id=str(current_user.id),
    )
    
    return task_to_response(task)
