"""Habit schemas for habit tracking and management."""

from datetime import datetime, time
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Frequency(str, Enum):
    """Habit frequency options."""
    
    DAILY = "daily"
    WEEKLY = "weekly"
    SPECIFIC_DAYS = "specific_days"
    X_PER_WEEK = "x_per_week"


class DayOfWeek(str, Enum):
    """Days of the week for specific_days frequency."""
    
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class HabitBase(BaseModel):
    """Base habit schema with common fields."""
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Habit title",
        examples=["Morning Meditation"]
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Detailed description of the habit",
        examples=["15 minutes of mindfulness meditation after waking up"]
    )
    icon: str = Field(
        default="🎯",
        max_length=10,
        description="Emoji icon for the habit",
        examples=["🧘", "💪", "📚"]
    )
    color: str = Field(
        default="#6366f1",
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Hex color code for the habit",
        examples=["#6366f1", "#10b981", "#f59e0b"]
    )
    frequency: Frequency = Field(
        default=Frequency.DAILY,
        description="How often the habit should be completed",
        examples=["daily", "weekly"]
    )
    specific_days: list[DayOfWeek] | None = Field(
        default=None,
        description="Days of the week for specific_days frequency",
        examples=[["monday", "wednesday", "friday"]]
    )
    times_per_week: int | None = Field(
        default=None,
        ge=1,
        le=7,
        description="Number of times per week for x_per_week frequency",
        examples=[3]
    )
    reminder_time: time | None = Field(
        default=None,
        description="Time to send reminder notification",
        examples=["08:00:00"]
    )
    base_xp: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Base XP reward for completing the habit",
        examples=[10, 25, 50]
    )
    base_coins: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Base coin reward for completing the habit",
        examples=[5, 10, 25]
    )
    
    @field_validator("specific_days")
    @classmethod
    def validate_specific_days(cls, v: list[DayOfWeek] | None, info) -> list[DayOfWeek] | None:
        """Validate specific_days is provided when frequency is specific_days."""
        if v is not None and len(v) == 0:
            raise ValueError("specific_days cannot be empty when provided")
        return v
    
    @field_validator("times_per_week")
    @classmethod
    def validate_times_per_week(cls, v: int | None, info) -> int | None:
        """Validate times_per_week is provided when frequency is x_per_week."""
        return v


class HabitCreate(HabitBase):
    """Schema for creating a new habit."""
    
    pass


class HabitUpdate(BaseModel):
    """Schema for updating an existing habit."""
    
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated habit title",
        examples=["Evening Meditation"]
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Updated description"
    )
    icon: str | None = Field(
        default=None,
        max_length=10,
        description="Updated emoji icon"
    )
    color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Updated hex color"
    )
    frequency: Frequency | None = Field(
        default=None,
        description="Updated frequency"
    )
    specific_days: list[DayOfWeek] | None = Field(
        default=None,
        description="Updated specific days"
    )
    times_per_week: int | None = Field(
        default=None,
        ge=1,
        le=7,
        description="Updated times per week"
    )
    reminder_time: time | None = Field(
        default=None,
        description="Updated reminder time"
    )
    is_active: bool | None = Field(
        default=None,
        description="Enable/disable the habit"
    )
    base_xp: int | None = Field(
        default=None,
        ge=1,
        le=100,
        description="Updated base XP"
    )
    base_coins: int | None = Field(
        default=None,
        ge=1,
        le=50,
        description="Updated base coins"
    )


class HabitResponse(HabitBase):
    """Schema for habit response with additional computed fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="Unique habit identifier",
        examples=["550e8400-e29b-41d4-a716-446655440001"]
    )
    user_id: UUID = Field(
        ...,
        description="Owner's user ID",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    current_streak: int = Field(
        default=0,
        ge=0,
        description="Current consecutive completion streak",
        examples=[7]
    )
    best_streak: int = Field(
        default=0,
        ge=0,
        description="Best streak ever achieved",
        examples=[30]
    )
    total_completions: int = Field(
        default=0,
        ge=0,
        description="Total times this habit was completed",
        examples=[150]
    )
    is_active: bool = Field(
        default=True,
        description="Whether the habit is currently active"
    )
    completed_today: bool = Field(
        default=False,
        description="Whether the habit was completed today"
    )
    created_at: datetime = Field(
        ...,
        description="When the habit was created",
        examples=["2024-01-15T10:30:00Z"]
    )
    updated_at: datetime = Field(
        ...,
        description="When the habit was last updated",
        examples=["2024-02-01T15:45:00Z"]
    )


class HabitWithProgress(HabitResponse):
    """Habit response with weekly progress information."""
    
    week_completions: int = Field(
        default=0,
        ge=0,
        description="Number of completions this week",
        examples=[5]
    )
    week_target: int = Field(
        default=7,
        ge=1,
        description="Target completions for this week",
        examples=[7]
    )
    progress_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Weekly progress as percentage",
        examples=[71.4]
    )
