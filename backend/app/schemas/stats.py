"""Stats schemas for analytics and insights."""

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TimeRange(str, Enum):
    """Time range options for statistics."""
    
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL_TIME = "all_time"


class CalendarDay(BaseModel):
    """Schema for a single day in the habit calendar."""
    
    date: date = Field(
        ...,
        description="The date",
        examples=["2024-02-09"]
    )
    habits_scheduled: int = Field(
        default=0,
        ge=0,
        description="Number of habits scheduled",
        examples=[5]
    )
    habits_completed: int = Field(
        default=0,
        ge=0,
        description="Number of habits completed",
        examples=[4]
    )
    tasks_completed: int = Field(
        default=0,
        ge=0,
        description="Number of tasks completed",
        examples=[3]
    )
    total_xp: int = Field(
        default=0,
        ge=0,
        description="Total XP earned",
        examples=[150]
    )
    total_coins: int = Field(
        default=0,
        ge=0,
        description="Total coins earned",
        examples=[75]
    )
    completion_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Completion percentage",
        examples=[80.0]
    )
    mood_average: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
        description="Average mood rating",
        examples=[4.2]
    )
    is_perfect_day: bool = Field(
        default=False,
        description="Whether all habits were completed"
    )


class HabitStat(BaseModel):
    """Statistics for a single habit."""
    
    habit_id: UUID = Field(
        ...,
        description="Habit identifier"
    )
    habit_name: str = Field(
        ...,
        description="Habit name"
    )
    icon: str = Field(
        ...,
        description="Habit icon"
    )
    total_completions: int = Field(
        default=0,
        ge=0,
        description="Total times completed"
    )
    current_streak: int = Field(
        default=0,
        ge=0,
        description="Current streak"
    )
    best_streak: int = Field(
        default=0,
        ge=0,
        description="Best streak ever"
    )
    completion_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Overall completion rate"
    )
    total_xp_earned: int = Field(
        default=0,
        ge=0,
        description="Total XP from this habit"
    )
    average_mood: float | None = Field(
        default=None,
        description="Average mood when completing"
    )


class StatsOverview(BaseModel):
    """Comprehensive statistics overview."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Time range
    time_range: TimeRange = Field(
        ...,
        description="Time range for these stats"
    )
    start_date: date = Field(
        ...,
        description="Start of the period"
    )
    end_date: date = Field(
        ...,
        description="End of the period"
    )
    
    # Overall stats
    total_habits: int = Field(
        default=0,
        ge=0,
        description="Total active habits"
    )
    total_tasks_completed: int = Field(
        default=0,
        ge=0,
        description="Tasks completed in period"
    )
    total_completions: int = Field(
        default=0,
        ge=0,
        description="Total habit completions"
    )
    total_xp_earned: int = Field(
        default=0,
        ge=0,
        description="Total XP earned"
    )
    total_coins_earned: int = Field(
        default=0,
        ge=0,
        description="Total coins earned"
    )
    
    # Rates
    overall_completion_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Overall habit completion rate",
        examples=[78.5]
    )
    perfect_days: int = Field(
        default=0,
        ge=0,
        description="Days with 100% completion"
    )
    days_with_activity: int = Field(
        default=0,
        ge=0,
        description="Days with at least one completion"
    )
    
    # Streaks
    current_streak: int = Field(
        default=0,
        ge=0,
        description="Current overall streak"
    )
    longest_streak: int = Field(
        default=0,
        ge=0,
        description="Longest streak in period"
    )
    
    # Best performers
    best_habit: HabitStat | None = Field(
        default=None,
        description="Habit with highest completion rate"
    )
    most_completed_habit: HabitStat | None = Field(
        default=None,
        description="Habit completed most often"
    )
    
    # Trends
    completion_trend: float = Field(
        default=0.0,
        description="Trend vs previous period (-100 to +100)",
        examples=[5.2, -3.1]
    )
    xp_trend: float = Field(
        default=0.0,
        description="XP trend vs previous period"
    )


class LeaderboardEntry(BaseModel):
    """Schema for a leaderboard entry."""
    
    rank: int = Field(
        ...,
        ge=1,
        description="Position on leaderboard",
        examples=[1, 2, 3]
    )
    user_id: UUID = Field(
        ...,
        description="User identifier"
    )
    username: str = Field(
        ...,
        description="Username",
        examples=["DragonSlayer42"]
    )
    avatar_url: str | None = Field(
        default=None,
        description="User avatar"
    )
    character_name: str | None = Field(
        default=None,
        description="Character name"
    )
    character_class: str | None = Field(
        default=None,
        description="Character class"
    )
    level: int = Field(
        ...,
        ge=1,
        description="User level"
    )
    score: int = Field(
        ...,
        ge=0,
        description="Leaderboard score",
        examples=[15420]
    )
    metric_value: float = Field(
        ...,
        description="The metric being ranked by",
        examples=[98.5, 1500]
    )
    metric_label: str = Field(
        ...,
        description="Label for the metric",
        examples=["XP", "Streak Days", "Completion %"]
    )
    is_current_user: bool = Field(
        default=False,
        description="Whether this is the requesting user"
    )
    is_friend: bool = Field(
        default=False,
        description="Whether this user is a friend"
    )


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard response."""
    
    leaderboard_type: str = Field(
        ...,
        description="Type of leaderboard",
        examples=["xp", "streak", "completions", "level"]
    )
    time_range: TimeRange = Field(
        ...,
        description="Time range for the leaderboard"
    )
    entries: list[LeaderboardEntry] = Field(
        default_factory=list,
        description="Leaderboard entries"
    )
    user_rank: int | None = Field(
        default=None,
        description="Current user's rank"
    )
    total_participants: int = Field(
        default=0,
        ge=0,
        description="Total users on leaderboard"
    )
    updated_at: datetime = Field(
        ...,
        description="When leaderboard was last updated"
    )


class InsightCategory(str, Enum):
    """Categories of AI-generated insights."""
    
    ACHIEVEMENT = "achievement"
    SUGGESTION = "suggestion"
    WARNING = "warning"
    TREND = "trend"
    MOTIVATION = "motivation"


class Insight(BaseModel):
    """AI-generated insight about user's habits."""
    
    id: UUID = Field(
        ...,
        description="Insight identifier"
    )
    category: InsightCategory = Field(
        ...,
        description="Type of insight"
    )
    title: str = Field(
        ...,
        max_length=100,
        description="Insight headline",
        examples=["🔥 Streak Master!"]
    )
    message: str = Field(
        ...,
        max_length=500,
        description="Detailed insight message",
        examples=["You've maintained a 7-day streak on Morning Meditation! Keep it up to unlock the 'Zen Master' badge."]
    )
    action_suggestion: str | None = Field(
        default=None,
        max_length=200,
        description="Suggested action",
        examples=["Try increasing your meditation time by 5 minutes"]
    )
    related_habit_id: UUID | None = Field(
        default=None,
        description="Related habit (if applicable)"
    )
    priority: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Importance (1=low, 5=critical)"
    )
    generated_at: datetime = Field(
        ...,
        description="When the insight was generated"
    )
    is_read: bool = Field(
        default=False,
        description="Whether user has seen this insight"
    )


class InsightsResponse(BaseModel):
    """Schema for insights response."""
    
    insights: list[Insight] = Field(
        default_factory=list,
        description="List of insights"
    )
    unread_count: int = Field(
        default=0,
        ge=0,
        description="Number of unread insights"
    )
    generated_at: datetime = Field(
        ...,
        description="When insights were generated"
    )


class CalendarResponse(BaseModel):
    """Schema for calendar view response."""
    
    month: int = Field(
        ...,
        ge=1,
        le=12,
        description="Month number"
    )
    year: int = Field(
        ...,
        ge=2020,
        description="Year"
    )
    days: list[CalendarDay] = Field(
        default_factory=list,
        description="Days in the month with data"
    )
    month_completion_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Average completion rate for the month"
    )
    perfect_days_count: int = Field(
        default=0,
        ge=0,
        description="Number of perfect days"
    )
    total_xp: int = Field(
        default=0,
        ge=0,
        description="Total XP earned in month"
    )
