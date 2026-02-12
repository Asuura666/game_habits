"""Calendar-specific schemas for completion heatmap."""

from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class CalendarDayData(BaseModel):
    """Data for a single day in the calendar heatmap."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    day_date: date = Field(
        ...,
        serialization_alias="date",
        description="The date",
        examples=["2026-02-01"]
    )
    completion_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Completion rate (0.0 to 1.0)",
        examples=[0.8]
    )
    habits_done: int = Field(
        default=0,
        ge=0,
        description="Number of habits completed this day",
        examples=[4]
    )
    habits_total: int = Field(
        default=0,
        ge=0,
        description="Total habits scheduled for this day",
        examples=[5]
    )
    xp_earned: int = Field(
        default=0,
        ge=0,
        description="Total XP earned this day",
        examples=[45]
    )


class CalendarSummary(BaseModel):
    """Summary statistics for the calendar month."""
    
    perfect_days: int = Field(
        default=0,
        ge=0,
        description="Number of days with 100% completion",
        examples=[12]
    )
    total_completions: int = Field(
        default=0,
        ge=0,
        description="Total habit completions in the month",
        examples=[89]
    )
    average_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average completion rate for the month",
        examples=[0.75]
    )


class CalendarResponse(BaseModel):
    """Response for the calendar endpoint."""
    
    month: str = Field(
        ...,
        description="Month in YYYY-MM format",
        examples=["2026-02"]
    )
    days: list[CalendarDayData] = Field(
        default_factory=list,
        description="List of daily completion data"
    )
    summary: CalendarSummary = Field(
        default_factory=CalendarSummary,
        description="Monthly summary statistics"
    )
