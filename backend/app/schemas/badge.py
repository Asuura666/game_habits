"""Badge schemas for achievements and unlockables."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BadgeCategory(str, Enum):
    """Categories of badges."""
    
    STREAK = "streak"              # Streak-related achievements
    COMPLETION = "completion"      # Completion milestones
    HABIT = "habit"                # Specific habit achievements
    SOCIAL = "social"              # Friend/community achievements
    COMBAT = "combat"              # PvP achievements
    SPECIAL = "special"            # Limited/seasonal badges
    PROGRESSION = "progression"    # Level/XP milestones


class BadgeTier(str, Enum):
    """Badge tier/difficulty levels."""
    
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class BadgeResponse(BaseModel):
    """Schema for badge definition."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="Unique badge identifier",
        examples=["550e8400-e29b-41d4-a716-446655440009"]
    )
    name: str = Field(
        ...,
        max_length=50,
        description="Badge name",
        examples=["Streak Master"]
    )
    description: str = Field(
        ...,
        max_length=200,
        description="How to earn this badge",
        examples=["Maintain a 30-day streak on any habit"]
    )
    icon: str = Field(
        ...,
        max_length=10,
        description="Badge emoji icon",
        examples=["🔥", "⭐", "🏆"]
    )
    image_url: str | None = Field(
        default=None,
        max_length=500,
        description="URL to badge image"
    )
    category: BadgeCategory = Field(
        ...,
        description="Badge category"
    )
    tier: BadgeTier = Field(
        ...,
        description="Badge difficulty tier"
    )
    xp_reward: int = Field(
        default=0,
        ge=0,
        description="XP awarded when earned",
        examples=[500]
    )
    coin_reward: int = Field(
        default=0,
        ge=0,
        description="Coins awarded when earned",
        examples=[250]
    )
    requirement_type: str = Field(
        ...,
        description="Type of requirement",
        examples=["streak_days", "total_completions", "level_reached"]
    )
    requirement_value: int = Field(
        ...,
        ge=1,
        description="Value needed to earn",
        examples=[30]
    )
    requirement_habit_id: UUID | None = Field(
        default=None,
        description="Specific habit required (if applicable)"
    )
    is_secret: bool = Field(
        default=False,
        description="Whether badge is hidden until earned"
    )
    is_limited: bool = Field(
        default=False,
        description="Whether badge is limited edition"
    )
    available_until: datetime | None = Field(
        default=None,
        description="When limited badge expires"
    )
    total_earners: int = Field(
        default=0,
        ge=0,
        description="Total users who have this badge"
    )
    rarity_percentage: float = Field(
        default=100.0,
        ge=0.0,
        le=100.0,
        description="Percentage of users who have this badge",
        examples=[5.2]
    )


class BadgeProgress(BaseModel):
    """Schema for progress toward a badge."""
    
    badge: BadgeResponse = Field(
        ...,
        description="The badge being tracked"
    )
    current_value: int = Field(
        default=0,
        ge=0,
        description="Current progress value",
        examples=[22]
    )
    target_value: int = Field(
        ...,
        ge=1,
        description="Value needed to earn",
        examples=[30]
    )
    progress_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Progress as percentage",
        examples=[73.3]
    )
    estimated_completion: datetime | None = Field(
        default=None,
        description="Estimated date of completion at current pace"
    )


class UserBadgeResponse(BaseModel):
    """Schema for a badge earned by a user."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="Unique user-badge record ID"
    )
    badge: BadgeResponse = Field(
        ...,
        description="The badge details"
    )
    earned_at: datetime = Field(
        ...,
        description="When the badge was earned",
        examples=["2024-02-09T10:30:00Z"]
    )
    is_displayed: bool = Field(
        default=False,
        description="Whether badge is displayed on profile"
    )
    is_favorite: bool = Field(
        default=False,
        description="Whether user marked as favorite"
    )


class BadgeShowcaseUpdate(BaseModel):
    """Schema for updating badge showcase/favorites."""
    
    badge_ids: list[UUID] = Field(
        ...,
        max_length=6,
        description="Up to 6 badge IDs to display on profile"
    )


class BadgeCollectionResponse(BaseModel):
    """Schema for user's badge collection."""
    
    earned_badges: list[UserBadgeResponse] = Field(
        default_factory=list,
        description="Badges the user has earned"
    )
    in_progress: list[BadgeProgress] = Field(
        default_factory=list,
        description="Badges being worked toward"
    )
    locked_badges: list[BadgeResponse] = Field(
        default_factory=list,
        description="Badges not yet started"
    )
    total_earned: int = Field(
        default=0,
        ge=0,
        description="Total badges earned"
    )
    total_available: int = Field(
        default=0,
        ge=0,
        description="Total badges available"
    )
    completion_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Percentage of badges earned"
    )
    showcase_badges: list[UserBadgeResponse] = Field(
        default_factory=list,
        max_length=6,
        description="Badges displayed on profile"
    )
    recent_badges: list[UserBadgeResponse] = Field(
        default_factory=list,
        max_length=5,
        description="Most recently earned badges"
    )


class BadgeNotification(BaseModel):
    """Schema for badge earned notification."""
    
    badge: BadgeResponse = Field(
        ...,
        description="The badge that was earned"
    )
    xp_earned: int = Field(
        default=0,
        ge=0,
        description="XP awarded"
    )
    coins_earned: int = Field(
        default=0,
        ge=0,
        description="Coins awarded"
    )
    message: str = Field(
        ...,
        description="Congratulatory message",
        examples=["🏆 Achievement Unlocked: Streak Master! You maintained a 30-day streak!"]
    )
    earned_at: datetime = Field(
        ...,
        description="When the badge was earned"
    )
