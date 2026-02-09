"""Completion schemas for tracking habit and task completions."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompletionType(str, Enum):
    """Type of completion (habit or task)."""
    
    HABIT = "habit"
    TASK = "task"


class CompletionCreate(BaseModel):
    """Schema for creating a completion record."""
    
    habit_id: UUID | None = Field(
        default=None,
        description="ID of the completed habit",
        examples=["550e8400-e29b-41d4-a716-446655440001"]
    )
    task_id: UUID | None = Field(
        default=None,
        description="ID of the completed task",
        examples=["550e8400-e29b-41d4-a716-446655440002"]
    )
    notes: str | None = Field(
        default=None,
        max_length=500,
        description="Optional notes about the completion",
        examples=["Meditated for 20 minutes instead of 15!"]
    )
    mood_rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="How the user felt (1-5 scale)",
        examples=[4]
    )
    difficulty_rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="How difficult it felt (1-5 scale)",
        examples=[3]
    )


class CompletionResult(BaseModel):
    """Result of completing a habit or task with rewards."""
    
    xp_earned: int = Field(
        ...,
        ge=0,
        description="Total XP earned including bonuses",
        examples=[45]
    )
    coins_earned: int = Field(
        ...,
        ge=0,
        description="Total coins earned including bonuses",
        examples=[22]
    )
    base_xp: int = Field(
        ...,
        ge=0,
        description="Base XP before multipliers",
        examples=[30]
    )
    base_coins: int = Field(
        ...,
        ge=0,
        description="Base coins before multipliers",
        examples=[15]
    )
    streak_multiplier: float = Field(
        default=1.0,
        ge=1.0,
        le=3.0,
        description="Multiplier from current streak",
        examples=[1.5]
    )
    streak_bonus_xp: int = Field(
        default=0,
        ge=0,
        description="Additional XP from streak bonus",
        examples=[15]
    )
    streak_bonus_coins: int = Field(
        default=0,
        ge=0,
        description="Additional coins from streak bonus",
        examples=[7]
    )
    new_streak: int = Field(
        ...,
        ge=0,
        description="Updated streak count",
        examples=[8]
    )
    is_personal_best: bool = Field(
        default=False,
        description="Whether this is a new personal best streak"
    )
    level_up: bool = Field(
        default=False,
        description="Whether the user leveled up"
    )
    new_level: int | None = Field(
        default=None,
        ge=1,
        description="New level if leveled up",
        examples=[16]
    )
    badges_earned: list[str] = Field(
        default_factory=list,
        description="List of badge IDs earned from this completion",
        examples=[["streak_7", "early_bird"]]
    )
    achievement_message: str | None = Field(
        default=None,
        description="Special achievement message to display",
        examples=["🔥 7-day streak! Keep it up!"]
    )


class CompletionResponse(BaseModel):
    """Schema for completion response with full details."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="Unique completion identifier",
        examples=["550e8400-e29b-41d4-a716-446655440003"]
    )
    user_id: UUID = Field(
        ...,
        description="User who completed"
    )
    completion_type: CompletionType = Field(
        ...,
        description="Whether this is a habit or task completion"
    )
    habit_id: UUID | None = Field(
        default=None,
        description="Completed habit ID (if habit)"
    )
    task_id: UUID | None = Field(
        default=None,
        description="Completed task ID (if task)"
    )
    xp_earned: int = Field(
        ...,
        ge=0,
        description="Total XP earned"
    )
    coins_earned: int = Field(
        ...,
        ge=0,
        description="Total coins earned"
    )
    streak_at_completion: int = Field(
        default=0,
        ge=0,
        description="Streak count at time of completion"
    )
    notes: str | None = Field(
        default=None,
        description="User notes"
    )
    mood_rating: int | None = Field(
        default=None,
        description="User's mood rating"
    )
    difficulty_rating: int | None = Field(
        default=None,
        description="User's difficulty rating"
    )
    completed_at: datetime = Field(
        ...,
        description="When the completion occurred",
        examples=["2024-02-09T08:30:00Z"]
    )


class CompletionWithResult(CompletionResponse):
    """Completion response including the reward calculation result."""
    
    result: CompletionResult = Field(
        ...,
        description="Detailed reward calculation"
    )


class DailyCompletionSummary(BaseModel):
    """Summary of completions for a single day."""
    
    date: datetime = Field(
        ...,
        description="The date of this summary"
    )
    habits_completed: int = Field(
        default=0,
        ge=0,
        description="Number of habits completed"
    )
    habits_total: int = Field(
        default=0,
        ge=0,
        description="Total habits scheduled for this day"
    )
    tasks_completed: int = Field(
        default=0,
        ge=0,
        description="Number of tasks completed"
    )
    total_xp: int = Field(
        default=0,
        ge=0,
        description="Total XP earned this day"
    )
    total_coins: int = Field(
        default=0,
        ge=0,
        description="Total coins earned this day"
    )
    completion_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Percentage of habits completed"
    )
