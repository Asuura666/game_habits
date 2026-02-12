"""User schemas for authentication and profile management."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["player@example.com"]
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Unique username",
        examples=["DragonSlayer42"]
    )
    
    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username contains only allowed characters."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores and hyphens allowed)")
        return v


class UserCreate(UserBase):
    """Schema for user registration."""
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User password (min 8 characters)",
        examples=["SecureP@ss123"]
    )
    
    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password meets strength requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["player@example.com"]
    )
    password: str = Field(
        ...,
        description="User password",
        examples=["SecureP@ss123"]
    )


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=30,
        description="New username",
        examples=["NewHeroName"]
    )
    email: EmailStr | None = Field(
        default=None,
        description="New email address",
        examples=["newemail@example.com"]
    )
    display_name: str | None = Field(
        default=None,
        max_length=100,
        description="Display name shown on profile",
        examples=["Dragon Slayer"]
    )
    bio: str | None = Field(
        default=None,
        max_length=280,
        description="Short bio/description",
        examples=["Slaying dragons and completing habits since 2026"]
    )
    avatar_url: str | None = Field(
        default=None,
        max_length=500,
        description="URL to user's avatar image",
        examples=["https://example.com/avatars/hero.png"]
    )
    timezone: str | None = Field(
        default=None,
        max_length=50,
        description="User's timezone",
        examples=["Europe/Paris"]
    )
    is_public: bool | None = Field(
        default=None,
        description="Whether profile is publicly visible"
    )
    notifications_enabled: bool | None = Field(
        default=None,
        description="Enable/disable notifications"
    )
    theme: str | None = Field(
        default=None,
        description="UI theme preference",
        examples=["dark", "light"]
    )


class UserResponse(BaseModel):
    """Schema for user response (public data)."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="Unique user identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["player@example.com"]
    )
    username: str = Field(
        ...,
        description="User's display name",
        examples=["DragonSlayer42"]
    )
    display_name: str | None = Field(
        default=None,
        description="Display name shown on profile"
    )
    bio: str | None = Field(
        default=None,
        description="Short bio/description"
    )
    avatar_url: str | None = Field(
        default=None,
        description="URL to user's avatar",
        examples=["https://example.com/avatars/hero.png"]
    )
    level: int = Field(
        default=1,
        ge=1,
        description="Current player level",
        examples=[15]
    )
    total_xp: int = Field(
        default=0,
        ge=0,
        description="Total experience points earned",
        examples=[4500]
    )
    coins: int = Field(
        default=0,
        ge=0,
        description="Current coin balance",
        examples=[1250]
    )
    current_streak: int = Field(
        default=0,
        ge=0,
        description="Current habit streak"
    )
    best_streak: int = Field(
        default=0,
        ge=0,
        description="Best streak ever achieved"
    )
    friend_code: str | None = Field(
        default=None,
        description="Unique friend code for adding friends",
        examples=["ABC123"]
    )
    is_public: bool = Field(
        default=False,
        description="Whether profile is publicly visible"
    )
    created_at: datetime = Field(
        ...,
        description="Account creation timestamp",
        examples=["2024-01-15T10:30:00Z"]
    )
    is_active: bool = Field(
        default=True,
        description="Whether the account is active"
    )


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str = Field(
        ...,
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
        examples=["bearer"]
    )
    expires_in: int = Field(
        default=3600,
        description="Token expiration time in seconds",
        examples=[3600]
    )
    user: UserResponse = Field(
        ...,
        description="Authenticated user data"
    )
