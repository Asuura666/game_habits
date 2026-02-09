"""Friend schemas for social features."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FriendshipStatus(str, Enum):
    """Status of a friendship/friend request."""
    
    PENDING = "pending"      # Request sent, awaiting response
    ACCEPTED = "accepted"    # Friends
    DECLINED = "declined"    # Request was declined
    BLOCKED = "blocked"      # User has blocked the other


class FriendRequest(BaseModel):
    """Schema for sending a friend request."""
    
    user_id: UUID | None = Field(
        default=None,
        description="User ID to send request to",
        examples=["550e8400-e29b-41d4-a716-446655440008"]
    )
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=30,
        description="Username to send request to (alternative to user_id)",
        examples=["DragonHeart"]
    )
    message: str | None = Field(
        default=None,
        max_length=200,
        description="Optional message with the request",
        examples=["Hey! Let's compete on habits together!"]
    )


class FriendRequestResponse(BaseModel):
    """Schema for friend request in response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="Friend request ID"
    )
    from_user_id: UUID = Field(
        ...,
        description="Who sent the request"
    )
    from_username: str = Field(
        ...,
        description="Sender's username"
    )
    from_avatar: str | None = Field(
        default=None,
        description="Sender's avatar URL"
    )
    from_level: int = Field(
        ...,
        description="Sender's level"
    )
    to_user_id: UUID = Field(
        ...,
        description="Who received the request"
    )
    message: str | None = Field(
        default=None,
        description="Request message"
    )
    status: FriendshipStatus = Field(
        ...,
        description="Request status"
    )
    created_at: datetime = Field(
        ...,
        description="When request was sent"
    )


class FriendResponse(BaseModel):
    """Schema for a friend in the friends list."""
    
    model_config = ConfigDict(from_attributes=True)
    
    friendship_id: UUID = Field(
        ...,
        description="Friendship record ID"
    )
    user_id: UUID = Field(
        ...,
        description="Friend's user ID"
    )
    username: str = Field(
        ...,
        description="Friend's username",
        examples=["DragonHeart"]
    )
    avatar_url: str | None = Field(
        default=None,
        description="Friend's avatar URL"
    )
    character_name: str | None = Field(
        default=None,
        description="Friend's character name",
        examples=["Flamebringer"]
    )
    character_class: str | None = Field(
        default=None,
        description="Friend's character class",
        examples=["mage"]
    )
    level: int = Field(
        ...,
        ge=1,
        description="Friend's current level",
        examples=[22]
    )
    total_xp: int = Field(
        default=0,
        ge=0,
        description="Friend's total XP"
    )
    current_streak: int = Field(
        default=0,
        ge=0,
        description="Friend's current streak",
        examples=[14]
    )
    is_online: bool = Field(
        default=False,
        description="Whether friend is currently online"
    )
    last_active: datetime | None = Field(
        default=None,
        description="When friend was last active"
    )
    friends_since: datetime = Field(
        ...,
        description="When the friendship started"
    )


class FriendActivity(BaseModel):
    """Schema for friend activity feed item."""
    
    id: UUID = Field(
        ...,
        description="Activity ID"
    )
    user_id: UUID = Field(
        ...,
        description="Friend who performed the activity"
    )
    username: str = Field(
        ...,
        description="Friend's username"
    )
    avatar_url: str | None = Field(
        default=None,
        description="Friend's avatar"
    )
    activity_type: str = Field(
        ...,
        description="Type of activity",
        examples=["habit_completed", "level_up", "badge_earned", "streak_milestone"]
    )
    activity_data: dict = Field(
        default_factory=dict,
        description="Activity-specific data",
        examples=[{"habit_name": "Morning Meditation", "streak": 7}]
    )
    message: str = Field(
        ...,
        description="Human-readable activity message",
        examples=["DragonHeart completed Morning Meditation (7-day streak!)"]
    )
    created_at: datetime = Field(
        ...,
        description="When the activity occurred"
    )


class FriendListResponse(BaseModel):
    """Schema for paginated friends list."""
    
    friends: list[FriendResponse] = Field(
        default_factory=list,
        description="List of friends"
    )
    total: int = Field(
        default=0,
        ge=0,
        description="Total number of friends"
    )
    online_count: int = Field(
        default=0,
        ge=0,
        description="Number of friends currently online"
    )


class PendingRequestsResponse(BaseModel):
    """Schema for pending friend requests."""
    
    incoming: list[FriendRequestResponse] = Field(
        default_factory=list,
        description="Requests received"
    )
    outgoing: list[FriendRequestResponse] = Field(
        default_factory=list,
        description="Requests sent"
    )
    incoming_count: int = Field(
        default=0,
        ge=0,
        description="Number of incoming requests"
    )
    outgoing_count: int = Field(
        default=0,
        ge=0,
        description="Number of outgoing requests"
    )


class FriendActionRequest(BaseModel):
    """Schema for accepting/declining friend requests."""
    
    request_id: UUID = Field(
        ...,
        description="Friend request ID to act on"
    )
    action: str = Field(
        ...,
        pattern="^(accept|decline)$",
        description="Action to take",
        examples=["accept", "decline"]
    )


class BlockUserRequest(BaseModel):
    """Schema for blocking a user."""
    
    user_id: UUID = Field(
        ...,
        description="User ID to block"
    )
    reason: str | None = Field(
        default=None,
        max_length=200,
        description="Optional reason for blocking"
    )
