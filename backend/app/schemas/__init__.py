"""
Pydantic schemas for the Habit Tracker API.

This module exports all schemas organized by domain.
"""

# User schemas
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse,
)

# Habit schemas
from app.schemas.habit import (
    Frequency,
    DayOfWeek,
    HabitBase,
    HabitCreate,
    HabitUpdate,
    HabitResponse,
    HabitWithProgress,
)

# Task schemas
from app.schemas.task import (
    Priority,
    Difficulty,
    TaskStatus,
    SubtaskBase,
    SubtaskCreate,
    SubtaskResponse,
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskEvaluation,
    TaskResponse,
    TaskWithEvaluation,
)

# Completion schemas
from app.schemas.completion import (
    CompletionType,
    CompletionCreate,
    CompletionResult,
    CompletionResponse,
    CompletionWithResult,
    CompletionBackfill,
    DailyCompletionSummary,
)

# Character schemas
from app.schemas.character import (
    ClassEnum,
    StatsDistribution,
    CharacterCreate,
    CharacterUpdate,
    StatPointAllocation,
    EquippedItems,
    CharacterResponse,
    CharacterSummary,
    LevelUpResult,
)

# Item schemas
from app.schemas.item import (
    ItemCategory,
    Rarity,
    ItemEffect,
    ItemBase,
    ItemResponse,
    InventoryItem,
    ShopCategory,
    PurchaseRequest,
    PurchaseResult,
)

# Combat schemas
from app.schemas.combat import (
    CombatStatus,
    CombatType,
    ActionType,
    ChallengeCreate,
    CombatParticipant,
    CombatAction,
    CombatTurn,
    CombatResult,
    CombatResponse,
    ChallengeResponse,
    PerformActionRequest,
)

# Friend schemas
from app.schemas.friend import (
    FriendshipStatus,
    FriendRequest,
    FriendRequestResponse,
    FriendResponse,
    FriendActivity,
    FriendListResponse,
    PendingRequestsResponse,
    FriendActionRequest,
    BlockUserRequest,
)

# Stats schemas
from app.schemas.stats import (
    TimeRange,
    CalendarDay,
    HabitStat,
    StatsOverview,
    LeaderboardEntry,
    LeaderboardResponse,
    InsightCategory,
    Insight,
    InsightsResponse,
    CalendarResponse,
)

# Badge schemas
from app.schemas.badge import (
    BadgeCategory,
    BadgeTier,
    BadgeResponse,
    BadgeProgress,
    UserBadgeResponse,
    BadgeShowcaseUpdate,
    BadgeCollectionResponse,
    BadgeNotification,
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "TokenResponse",
    # Habit
    "Frequency",
    "DayOfWeek",
    "HabitBase",
    "HabitCreate",
    "HabitUpdate",
    "HabitResponse",
    "HabitWithProgress",
    # Task
    "Priority",
    "Difficulty",
    "TaskStatus",
    "SubtaskBase",
    "SubtaskCreate",
    "SubtaskResponse",
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskEvaluation",
    "TaskResponse",
    "TaskWithEvaluation",
    # Completion
    "CompletionType",
    "CompletionCreate",
    "CompletionResult",
    "CompletionResponse",
    "CompletionWithResult",
    "DailyCompletionSummary",
    # Character
    "ClassEnum",
    "StatsDistribution",
    "CharacterCreate",
    "CharacterUpdate",
    "StatPointAllocation",
    "EquippedItems",
    "CharacterResponse",
    "CharacterSummary",
    "LevelUpResult",
    # Item
    "ItemCategory",
    "Rarity",
    "ItemEffect",
    "ItemBase",
    "ItemResponse",
    "InventoryItem",
    "ShopCategory",
    "PurchaseRequest",
    "PurchaseResult",
    # Combat
    "CombatStatus",
    "CombatType",
    "ActionType",
    "ChallengeCreate",
    "CombatParticipant",
    "CombatAction",
    "CombatTurn",
    "CombatResult",
    "CombatResponse",
    "ChallengeResponse",
    "PerformActionRequest",
    # Friend
    "FriendshipStatus",
    "FriendRequest",
    "FriendRequestResponse",
    "FriendResponse",
    "FriendActivity",
    "FriendListResponse",
    "PendingRequestsResponse",
    "FriendActionRequest",
    "BlockUserRequest",
    # Stats
    "TimeRange",
    "CalendarDay",
    "HabitStat",
    "StatsOverview",
    "LeaderboardEntry",
    "LeaderboardResponse",
    "InsightCategory",
    "Insight",
    "InsightsResponse",
    "CalendarResponse",
    # Badge
    "BadgeCategory",
    "BadgeTier",
    "BadgeResponse",
    "BadgeProgress",
    "UserBadgeResponse",
    "BadgeShowcaseUpdate",
    "BadgeCollectionResponse",
    "BadgeNotification",
]
