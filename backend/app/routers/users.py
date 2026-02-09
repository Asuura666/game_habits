"""Users router for profile management and admin operations."""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.utils.dependencies import (
    AdminUser,
    CurrentActiveUser,
    DatabaseSession,
    OptionalUser,
)

router = APIRouter(prefix="/users", tags=["Users"])


class UserListResponse(BaseModel):
    """Response schema for paginated user list."""
    
    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class DeleteAccountRequest(BaseModel):
    """Request schema for account deletion."""
    
    password: str | None = Field(
        default=None,
        description="Current password for verification (required for password-based accounts)"
    )
    confirm: bool = Field(
        ...,
        description="Confirmation flag (must be true)"
    )


class MessageResponse(BaseModel):
    """Simple message response."""
    
    message: str = Field(..., description="Response message")


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List all users (Admin)",
    description="Get a paginated list of all users. Requires admin access.",
)
async def list_users(
    admin: AdminUser,
    db: DatabaseSession,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    search: Annotated[str | None, Query(description="Search by username or email")] = None,
    active_only: Annotated[bool, Query(description="Only show active users")] = True,
) -> UserListResponse:
    """Get a paginated list of all users.
    
    Args:
        admin: The admin user making the request.
        db: Database session.
        page: Page number (1-indexed).
        page_size: Number of items per page.
        search: Optional search term for username/email.
        active_only: Whether to exclude deleted users.
        
    Returns:
        Paginated list of users.
    """
    # Build base query
    query = select(User)
    count_query = select(func.count(User.id))
    
    # Apply filters
    if active_only:
        query = query.where(User.deleted_at.is_(None))
        count_query = count_query.where(User.deleted_at.is_(None))
    
    if search:
        search_filter = (
            User.username.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Calculate pagination
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    offset = (page - 1) * page_size
    
    # Get users
    query = query.order_by(User.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get my profile",
    description="Get the current user's profile.",
)
async def get_my_profile(
    current_user: CurrentActiveUser,
) -> UserResponse:
    """Get the current user's profile.
    
    Args:
        current_user: The authenticated user.
        
    Returns:
        User profile data.
    """
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update my profile",
    description="Update the current user's profile.",
)
async def update_my_profile(
    current_user: CurrentActiveUser,
    user_update: UserUpdate,
    db: DatabaseSession,
) -> UserResponse:
    """Update the current user's profile.
    
    Args:
        current_user: The authenticated user.
        user_update: Profile update data.
        db: Database session.
        
    Returns:
        Updated user profile.
        
    Raises:
        HTTPException: 400 if username or email is already taken.
    """
    # Check if username is being changed and is available
    if user_update.username and user_update.username != current_user.username:
        result = await db.execute(
            select(User).where(
                User.username == user_update.username,
                User.id != current_user.id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
    
    # Check if email is being changed and is available
    if user_update.email and user_update.email != current_user.email:
        result = await db.execute(
            select(User).where(
                User.email == user_update.email,
                User.id != current_user.id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Update fields
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    await db.flush()
    await db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Delete my account",
    description="Soft delete the current user's account.",
)
async def delete_my_account(
    current_user: CurrentActiveUser,
    request: DeleteAccountRequest,
    db: DatabaseSession,
) -> MessageResponse:
    """Soft delete the current user's account.
    
    Args:
        current_user: The authenticated user.
        request: Deletion confirmation.
        db: Database session.
        
    Returns:
        Success message.
        
    Raises:
        HTTPException: 400 if confirmation is missing or password is wrong.
    """
    from app.utils.security import verify_password
    
    if not request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must confirm account deletion",
        )
    
    # Verify password for password-based accounts
    if current_user.password_hash:
        if not request.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password required for account deletion",
            )
        if not verify_password(request.password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password",
            )
    
    # Soft delete - set deleted_at timestamp
    current_user.deleted_at = datetime.now(timezone.utc)
    
    # Anonymize sensitive data (GDPR compliance)
    current_user.email = f"deleted_{current_user.id}@deleted.local"
    current_user.username = f"deleted_{str(current_user.id)[:8]}"
    current_user.password_hash = None
    current_user.google_id = None
    current_user.apple_id = None
    current_user.avatar_url = None
    current_user.bio = None
    
    await db.flush()
    
    return MessageResponse(message="Your account has been deleted")


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user profile",
    description="Get a user's public profile by ID.",
)
async def get_user_profile(
    user_id: UUID,
    db: DatabaseSession,
    current_user: OptionalUser = None,
) -> UserResponse:
    """Get a user's public profile.
    
    Args:
        user_id: The user's UUID.
        db: Database session.
        current_user: Optional authenticated user.
        
    Returns:
        User profile data (public fields only for non-owner).
        
    Raises:
        HTTPException: 404 if user not found.
        HTTPException: 403 if profile is private and viewer is not the owner.
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if profile is public or if viewer is the owner
    is_owner = current_user and current_user.id == user.id
    
    if not user.is_public and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This profile is private",
        )
    
    return UserResponse.model_validate(user)


@router.get(
    "/friend-code/{friend_code}",
    response_model=UserResponse,
    summary="Find user by friend code",
    description="Find a user by their friend code.",
)
async def get_user_by_friend_code(
    friend_code: str,
    db: DatabaseSession,
    current_user: CurrentActiveUser,
) -> UserResponse:
    """Find a user by their friend code.
    
    Args:
        friend_code: The user's unique friend code.
        db: Database session.
        current_user: The authenticated user making the request.
        
    Returns:
        User profile data.
        
    Raises:
        HTTPException: 404 if user not found.
    """
    result = await db.execute(
        select(User).where(
            User.friend_code == friend_code.upper(),
            User.deleted_at.is_(None)
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with this friend code",
        )
    
    return UserResponse.model_validate(user)
