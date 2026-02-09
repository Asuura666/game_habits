"""Task schemas for one-time tasks and AI evaluation."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Priority(str, Enum):
    """Task priority levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Difficulty(str, Enum):
    """Task difficulty levels with associated XP multipliers."""
    
    TRIVIAL = "trivial"      # 0.5x XP
    EASY = "easy"            # 1x XP
    MEDIUM = "medium"        # 1.5x XP
    HARD = "hard"            # 2x XP
    EPIC = "epic"            # 3x XP
    LEGENDARY = "legendary"  # 5x XP


class TaskStatus(str, Enum):
    """Task completion status."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SubtaskBase(BaseModel):
    """Base schema for subtasks."""
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Subtask title",
        examples=["Research existing solutions"]
    )
    is_completed: bool = Field(
        default=False,
        description="Whether the subtask is completed"
    )


class SubtaskCreate(SubtaskBase):
    """Schema for creating a subtask."""
    
    pass


class SubtaskResponse(SubtaskBase):
    """Schema for subtask response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="Unique subtask identifier"
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the subtask was completed"
    )


class TaskBase(BaseModel):
    """Base task schema with common fields."""
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title",
        examples=["Complete project proposal"]
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Detailed task description",
        examples=["Write a comprehensive proposal including timeline, budget, and deliverables"]
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Task priority level",
        examples=["high", "medium"]
    )
    due_date: datetime | None = Field(
        default=None,
        description="Task due date and time",
        examples=["2024-02-15T17:00:00Z"]
    )
    tags: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Task tags for categorization",
        examples=[["work", "important", "q1"]]
    )
    
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate and normalize tags."""
        return [tag.lower().strip() for tag in v if tag.strip()]


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    
    difficulty: Difficulty | None = Field(
        default=None,
        description="Manual difficulty override (if not using AI evaluation)",
        examples=["medium", "hard"]
    )
    xp_reward: int | None = Field(
        default=None,
        ge=1,
        le=1000,
        description="Manual XP reward override",
        examples=[50]
    )
    coins_reward: int | None = Field(
        default=None,
        ge=1,
        le=500,
        description="Manual coins reward override",
        examples=[25]
    )
    subtasks: list[SubtaskCreate] = Field(
        default_factory=list,
        max_length=20,
        description="Optional subtasks"
    )
    use_ai_evaluation: bool = Field(
        default=True,
        description="Whether to use AI to evaluate difficulty and rewards"
    )


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Updated task title"
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Updated description"
    )
    priority: Priority | None = Field(
        default=None,
        description="Updated priority"
    )
    difficulty: Difficulty | None = Field(
        default=None,
        description="Updated difficulty"
    )
    due_date: datetime | None = Field(
        default=None,
        description="Updated due date"
    )
    tags: list[str] | None = Field(
        default=None,
        max_length=10,
        description="Updated tags"
    )
    status: TaskStatus | None = Field(
        default=None,
        description="Updated status"
    )


class TaskEvaluation(BaseModel):
    """AI-generated task evaluation with difficulty and rewards."""
    
    difficulty: Difficulty = Field(
        ...,
        description="AI-assessed difficulty level",
        examples=["medium"]
    )
    xp_reward: int = Field(
        ...,
        ge=1,
        le=1000,
        description="Recommended XP reward based on difficulty",
        examples=[75]
    )
    coins_reward: int = Field(
        ...,
        ge=1,
        le=500,
        description="Recommended coin reward",
        examples=[35]
    )
    reasoning: str = Field(
        ...,
        max_length=500,
        description="AI explanation for the evaluation",
        examples=["This task requires moderate research and writing skills, estimated 2-4 hours of focused work."]
    )
    suggested_subtasks: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="AI-suggested subtasks to break down the work",
        examples=[["Research competitors", "Draft outline", "Write first draft", "Review and edit"]]
    )
    estimated_time_minutes: int = Field(
        ...,
        ge=5,
        le=480,
        description="Estimated time to complete in minutes",
        examples=[120]
    )


class TaskResponse(TaskBase):
    """Schema for task response with all fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="Unique task identifier",
        examples=["550e8400-e29b-41d4-a716-446655440002"]
    )
    user_id: UUID = Field(
        ...,
        description="Owner's user ID"
    )
    difficulty: Difficulty = Field(
        ...,
        description="Task difficulty (AI-evaluated or manual)",
        examples=["medium"]
    )
    xp_reward: int = Field(
        ...,
        ge=1,
        description="XP reward for completion",
        examples=[75]
    )
    coins_reward: int = Field(
        ...,
        ge=1,
        description="Coin reward for completion",
        examples=[35]
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Current task status"
    )
    subtasks: list[SubtaskResponse] = Field(
        default_factory=list,
        description="List of subtasks"
    )
    subtasks_completed: int = Field(
        default=0,
        ge=0,
        description="Number of completed subtasks"
    )
    subtasks_total: int = Field(
        default=0,
        ge=0,
        description="Total number of subtasks"
    )
    ai_reasoning: str | None = Field(
        default=None,
        description="AI evaluation reasoning (if AI-evaluated)"
    )
    estimated_time_minutes: int | None = Field(
        default=None,
        description="Estimated completion time"
    )
    created_at: datetime = Field(
        ...,
        description="When the task was created"
    )
    updated_at: datetime = Field(
        ...,
        description="When the task was last updated"
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the task was completed"
    )


class TaskWithEvaluation(TaskResponse):
    """Task response including the full AI evaluation."""
    
    evaluation: TaskEvaluation | None = Field(
        default=None,
        description="Full AI evaluation details"
    )
