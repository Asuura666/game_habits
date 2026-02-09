"""
Friends Router - Social Features

Endpoints for managing friendships:
- List friends
- Send/accept/reject friend requests
- Add by friend code
"""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.friendship import Friendship
from app.models.user import User
from app.schemas.friend import (
    FriendListResponse,
    FriendRequestResponse,
    FriendResponse,
    FriendshipStatus,
    PendingRequestsResponse,
)
from app.utils.auth import CurrentUser

logger = structlog.get_logger()

router = APIRouter(prefix="/friends", tags=["friends"])


# ============================================================================
# Helper Functions
# ============================================================================


async def get_friend_ids(db: AsyncSession, user_id: UUID) -> list[UUID]:
    """Get list of friend user IDs for a user."""
    result = await db.execute(
        select(Friendship).where(
            and_(
                or_(
                    Friendship.requester_id == user_id,
                    Friendship.addressee_id == user_id,
                ),
                Friendship.status == "accepted",
            )
        )
    )
    friendships = result.scalars().all()
    
    friend_ids = []
    for f in friendships:
        friend_id = f.addressee_id if f.requester_id == user_id else f.requester_id
        friend_ids.append(friend_id)
    
    return friend_ids


def build_friend_response(friendship: Friendship, current_user_id: UUID, friend: User) -> FriendResponse:
    """Build a FriendResponse from a Friendship and User."""
    return FriendResponse(
        friendship_id=friendship.id,
        user_id=friend.id,
        username=friend.username,
        avatar_url=friend.avatar_url,
        character_name=friend.character.name if friend.character else None,
        character_class=friend.character.character_class if friend.character else None,
        level=friend.level,
        total_xp=friend.total_xp,
        current_streak=friend.current_streak,
        is_online=False,  # Would need WebSocket tracking for real-time
        last_active=friend.last_login_at,
        friends_since=friendship.created_at,
    )


def build_request_response(
    friendship: Friendship,
    from_user: User,
    to_user: User,
) -> FriendRequestResponse:
    """Build a FriendRequestResponse from a Friendship."""
    return FriendRequestResponse(
        id=friendship.id,
        from_user_id=from_user.id,
        from_username=from_user.username,
        from_avatar=from_user.avatar_url,
        from_level=from_user.level,
        to_user_id=to_user.id,
        message=None,  # Message not stored in current model
        status=FriendshipStatus(friendship.status),
        created_at=friendship.created_at,
    )


# ============================================================================
# Endpoints
# ============================================================================


@router.get(
    "/",
    response_model=FriendListResponse,
    summary="List Friends",
    description="Get the current user's friends list with their stats",
)
async def list_friends(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> FriendListResponse:
    """Get paginated list of friends."""
    # Get accepted friendships
    result = await db.execute(
        select(Friendship).where(
            and_(
                or_(
                    Friendship.requester_id == current_user.id,
                    Friendship.addressee_id == current_user.id,
                ),
                Friendship.status == "accepted",
            )
        ).offset(offset).limit(limit)
    )
    friendships = result.scalars().all()
    
    # Build friend list
    friends = []
    online_count = 0
    
    for friendship in friendships:
        # Determine friend ID
        friend_id = (
            friendship.addressee_id
            if friendship.requester_id == current_user.id
            else friendship.requester_id
        )
        
        # Fetch friend user
        friend_result = await db.execute(
            select(User).where(User.id == friend_id)
        )
        friend = friend_result.scalar_one_or_none()
        
        if friend:
            friend_response = build_friend_response(friendship, current_user.id, friend)
            friends.append(friend_response)
            if friend_response.is_online:
                online_count += 1
    
    # Get total count
    count_result = await db.execute(
        select(Friendship).where(
            and_(
                or_(
                    Friendship.requester_id == current_user.id,
                    Friendship.addressee_id == current_user.id,
                ),
                Friendship.status == "accepted",
            )
        )
    )
    total = len(count_result.scalars().all())
    
    return FriendListResponse(
        friends=friends,
        total=total,
        online_count=online_count,
    )


@router.post(
    "/request/{user_id}",
    response_model=FriendRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send Friend Request",
    description="Send a friend request to another user by their ID",
)
async def send_friend_request(
    user_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> FriendRequestResponse:
    """Send a friend request to a user."""
    # Can't friend yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot send a friend request to yourself",
        )
    
    # Check target user exists
    target_result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    target_user = target_result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check existing friendship/request
    existing = await db.execute(
        select(Friendship).where(
            or_(
                and_(
                    Friendship.requester_id == current_user.id,
                    Friendship.addressee_id == user_id,
                ),
                and_(
                    Friendship.requester_id == user_id,
                    Friendship.addressee_id == current_user.id,
                ),
            )
        )
    )
    existing_friendship = existing.scalar_one_or_none()
    
    if existing_friendship:
        if existing_friendship.status == "accepted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already friends with this user",
            )
        elif existing_friendship.status == "pending":
            # If they sent us a request, auto-accept
            if existing_friendship.requester_id == user_id:
                existing_friendship.accept()
                await db.flush()
                return build_request_response(
                    existing_friendship, target_user, current_user
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Friend request already pending",
            )
        elif existing_friendship.status == "blocked":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot send request to this user",
            )
    
    # Create new request
    friendship = Friendship(
        requester_id=current_user.id,
        addressee_id=user_id,
        status="pending",
    )
    db.add(friendship)
    await db.flush()
    await db.refresh(friendship)
    
    logger.info(
        "Friend request sent",
        requester_id=str(current_user.id),
        addressee_id=str(user_id),
    )
    
    return build_request_response(friendship, current_user, target_user)


@router.post(
    "/accept/{request_id}",
    response_model=FriendResponse,
    summary="Accept Friend Request",
    description="Accept a pending friend request",
)
async def accept_friend_request(
    request_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> FriendResponse:
    """Accept a friend request."""
    # Find the request
    result = await db.execute(
        select(Friendship).where(
            Friendship.id == request_id,
            Friendship.addressee_id == current_user.id,
            Friendship.status == "pending",
        )
    )
    friendship = result.scalar_one_or_none()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found",
        )
    
    # Accept the request
    friendship.accept()
    await db.flush()
    
    # Get requester info
    requester_result = await db.execute(
        select(User).where(User.id == friendship.requester_id)
    )
    requester = requester_result.scalar_one()
    
    logger.info(
        "Friend request accepted",
        friendship_id=str(request_id),
        user_id=str(current_user.id),
    )
    
    return build_friend_response(friendship, current_user.id, requester)


@router.post(
    "/reject/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reject Friend Request",
    description="Reject a pending friend request",
)
async def reject_friend_request(
    request_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Reject a friend request."""
    # Find the request
    result = await db.execute(
        select(Friendship).where(
            Friendship.id == request_id,
            Friendship.addressee_id == current_user.id,
            Friendship.status == "pending",
        )
    )
    friendship = result.scalar_one_or_none()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found",
        )
    
    # Reject (or delete) the request
    friendship.reject()
    await db.flush()
    
    logger.info(
        "Friend request rejected",
        friendship_id=str(request_id),
        user_id=str(current_user.id),
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Friend",
    description="Remove a friend from your friends list",
)
async def remove_friend(
    user_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a friend."""
    # Find the friendship
    result = await db.execute(
        select(Friendship).where(
            and_(
                or_(
                    and_(
                        Friendship.requester_id == current_user.id,
                        Friendship.addressee_id == user_id,
                    ),
                    and_(
                        Friendship.requester_id == user_id,
                        Friendship.addressee_id == current_user.id,
                    ),
                ),
                Friendship.status == "accepted",
            )
        )
    )
    friendship = result.scalar_one_or_none()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found",
        )
    
    # Delete the friendship
    await db.delete(friendship)
    await db.flush()
    
    logger.info(
        "Friend removed",
        user_id=str(current_user.id),
        removed_user_id=str(user_id),
    )


@router.get(
    "/pending",
    response_model=PendingRequestsResponse,
    summary="Get Pending Requests",
    description="Get incoming and outgoing pending friend requests",
)
async def get_pending_requests(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> PendingRequestsResponse:
    """Get all pending friend requests."""
    # Incoming requests
    incoming_result = await db.execute(
        select(Friendship).where(
            Friendship.addressee_id == current_user.id,
            Friendship.status == "pending",
        )
    )
    incoming_friendships = incoming_result.scalars().all()
    
    incoming = []
    for f in incoming_friendships:
        requester_result = await db.execute(
            select(User).where(User.id == f.requester_id)
        )
        requester = requester_result.scalar_one()
        incoming.append(build_request_response(f, requester, current_user))
    
    # Outgoing requests
    outgoing_result = await db.execute(
        select(Friendship).where(
            Friendship.requester_id == current_user.id,
            Friendship.status == "pending",
        )
    )
    outgoing_friendships = outgoing_result.scalars().all()
    
    outgoing = []
    for f in outgoing_friendships:
        addressee_result = await db.execute(
            select(User).where(User.id == f.addressee_id)
        )
        addressee = addressee_result.scalar_one()
        outgoing.append(build_request_response(f, current_user, addressee))
    
    return PendingRequestsResponse(
        incoming=incoming,
        outgoing=outgoing,
        incoming_count=len(incoming),
        outgoing_count=len(outgoing),
    )


@router.get(
    "/code",
    summary="Get Friend Code",
    description="Get your unique friend code for sharing",
)
async def get_friend_code(
    current_user: CurrentUser,
) -> dict:
    """Get the current user's friend code."""
    return {
        "friend_code": current_user.friend_code,
        "username": current_user.username,
    }


@router.post(
    "/code/{code}",
    response_model=FriendRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add by Friend Code",
    description="Send a friend request using someone's friend code",
)
async def add_by_friend_code(
    code: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> FriendRequestResponse:
    """Send a friend request using a friend code."""
    # Find user by friend code
    result = await db.execute(
        select(User).where(
            User.friend_code == code.upper(),
            User.deleted_at.is_(None),
        )
    )
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid friend code",
        )
    
    # Can't friend yourself
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot add yourself as a friend",
        )
    
    # Check existing friendship/request
    existing = await db.execute(
        select(Friendship).where(
            or_(
                and_(
                    Friendship.requester_id == current_user.id,
                    Friendship.addressee_id == target_user.id,
                ),
                and_(
                    Friendship.requester_id == target_user.id,
                    Friendship.addressee_id == current_user.id,
                ),
            )
        )
    )
    existing_friendship = existing.scalar_one_or_none()
    
    if existing_friendship:
        if existing_friendship.status == "accepted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already friends with this user",
            )
        elif existing_friendship.status == "pending":
            # If they sent us a request, auto-accept
            if existing_friendship.requester_id == target_user.id:
                existing_friendship.accept()
                await db.flush()
                return build_request_response(
                    existing_friendship, target_user, current_user
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Friend request already pending",
            )
        elif existing_friendship.status == "blocked":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot send request to this user",
            )
    
    # Create new request
    friendship = Friendship(
        requester_id=current_user.id,
        addressee_id=target_user.id,
        status="pending",
    )
    db.add(friendship)
    await db.flush()
    await db.refresh(friendship)
    
    logger.info(
        "Friend request sent via code",
        requester_id=str(current_user.id),
        addressee_id=str(target_user.id),
        friend_code=code,
    )
    
    return build_request_response(friendship, current_user, target_user)
