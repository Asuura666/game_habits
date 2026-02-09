"""Authentication router for login, registration, and OAuth."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.utils.dependencies import CurrentActiveUser, DatabaseSession
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Additional schemas for auth endpoints
class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""
    
    refresh_token: str = Field(
        ...,
        description="JWT refresh token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )


class RefreshTokenResponse(BaseModel):
    """Response schema for token refresh."""
    
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=3600, description="Token expiration in seconds")


class OAuthRequest(BaseModel):
    """Request schema for OAuth authentication."""
    
    id_token: str = Field(
        ...,
        description="OAuth ID token from provider",
        examples=["eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )


class ForgotPasswordRequest(BaseModel):
    """Request schema for forgot password."""
    
    email: EmailStr = Field(
        ...,
        description="Email address to send reset link",
        examples=["player@example.com"]
    )


class ResetPasswordRequest(BaseModel):
    """Request schema for password reset."""
    
    token: str = Field(
        ...,
        description="Password reset token from email"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="New password (min 8 characters)"
    )


class MessageResponse(BaseModel):
    """Simple message response."""
    
    message: str = Field(..., description="Response message")


def _generate_friend_code() -> str:
    """Generate a unique friend code."""
    return secrets.token_hex(4).upper()


def _create_token_response(user: User, expires_minutes: int = 43200) -> TokenResponse:
    """Create a token response for a user."""
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=expires_minutes)
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_minutes * 60,
        user=UserResponse.model_validate(user)
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password.",
)
async def register(
    user_data: UserCreate,
    db: DatabaseSession,
) -> TokenResponse:
    """Register a new user with email and password.
    
    Args:
        user_data: User registration data.
        db: Database session.
        
    Returns:
        TokenResponse with access token and user data.
        
    Raises:
        HTTPException: 400 if email or username already exists.
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        friend_code=_generate_friend_code(),
    )
    
    db.add(user)
    await db.flush()
    await db.refresh(user)
    
    return _create_token_response(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    description="Authenticate user and return JWT access token.",
)
async def login(
    credentials: UserLogin,
    db: DatabaseSession,
) -> TokenResponse:
    """Login with email and password.
    
    Args:
        credentials: User login credentials.
        db: Database session.
        
    Returns:
        TokenResponse with access token and user data.
        
    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account has been deleted",
        )
    
    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()
    
    return _create_token_response(user)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout current user",
    description="Invalidate the current session. Client should discard tokens.",
)
async def logout(
    current_user: CurrentActiveUser,
) -> MessageResponse:
    """Logout the current user.
    
    Note:
        JWT tokens are stateless. This endpoint serves as a signal
        for the client to discard tokens. For true invalidation,
        implement a token blacklist with Redis.
    
    Args:
        current_user: The authenticated user.
        
    Returns:
        Success message.
    """
    # TODO: Add token to Redis blacklist for true invalidation
    return MessageResponse(message="Successfully logged out")


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh access token",
    description="Get a new access token using a refresh token.",
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: DatabaseSession,
) -> RefreshTokenResponse:
    """Refresh an access token using a refresh token.
    
    Args:
        request: Refresh token request.
        db: Database session.
        
    Returns:
        New access token.
        
    Raises:
        HTTPException: 401 if refresh token is invalid.
    """
    payload = verify_refresh_token(request.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Verify user still exists and is active
    from uuid import UUID
    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=43200 * 60,  # 30 days in seconds
    )


@router.post(
    "/google",
    response_model=TokenResponse,
    summary="Login with Google",
    description="Authenticate using Google OAuth ID token.",
)
async def google_auth(
    request: OAuthRequest,
    db: DatabaseSession,
) -> TokenResponse:
    """Authenticate or register using Google OAuth.
    
    Args:
        request: Google OAuth ID token.
        db: Database session.
        
    Returns:
        TokenResponse with access token and user data.
        
    Raises:
        HTTPException: 400 if token is invalid or verification fails.
    """
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests
    from app.config import get_settings
    
    settings = get_settings()
    
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured",
        )
    
    try:
        # Verify the Google ID token
        idinfo = google_id_token.verify_oauth2_token(
            request.id_token,
            google_requests.Request(),
            settings.google_client_id
        )
        
        google_id = idinfo["sub"]
        email = idinfo.get("email")
        name = idinfo.get("name", email.split("@")[0] if email else "User")
        picture = idinfo.get("picture")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Google token: {str(e)}",
        )
    
    # Check if user exists by Google ID
    result = await db.execute(
        select(User).where(User.google_id == google_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Check if email already exists
        result = await db.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # Link Google account to existing user
            existing_user.google_id = google_id
            if picture and not existing_user.avatar_url:
                existing_user.avatar_url = picture
            user = existing_user
        else:
            # Create new user
            # Generate unique username from name
            base_username = name.replace(" ", "").lower()[:20]
            username = base_username
            counter = 1
            
            while True:
                result = await db.execute(
                    select(User).where(User.username == username)
                )
                if not result.scalar_one_or_none():
                    break
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User(
                email=email,
                username=username,
                google_id=google_id,
                avatar_url=picture,
                friend_code=_generate_friend_code(),
            )
            db.add(user)
    
    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(user)
    
    return _create_token_response(user)


@router.post(
    "/apple",
    response_model=TokenResponse,
    summary="Login with Apple",
    description="Authenticate using Apple Sign In ID token.",
)
async def apple_auth(
    request: OAuthRequest,
    db: DatabaseSession,
) -> TokenResponse:
    """Authenticate or register using Apple Sign In.
    
    Args:
        request: Apple Sign In ID token.
        db: Database session.
        
    Returns:
        TokenResponse with access token and user data.
        
    Raises:
        HTTPException: 400 if token is invalid or verification fails.
    """
    import jwt
    from app.config import get_settings
    
    settings = get_settings()
    
    if not settings.apple_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Apple Sign In not configured",
        )
    
    try:
        # Decode Apple ID token (simplified - production should verify with Apple's public keys)
        # In production, fetch Apple's public keys from https://appleid.apple.com/auth/keys
        unverified = jwt.decode(request.id_token, options={"verify_signature": False})
        
        apple_id = unverified.get("sub")
        email = unverified.get("email")
        
        if not apple_id:
            raise ValueError("Missing Apple user ID")
            
    except jwt.DecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Apple token: {str(e)}",
        )
    
    # Check if user exists by Apple ID
    result = await db.execute(
        select(User).where(User.apple_id == apple_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Check if email exists (Apple may not always provide email)
        if email:
            result = await db.execute(
                select(User).where(User.email == email)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                existing_user.apple_id = apple_id
                user = existing_user
        
        if not user:
            # Create new user
            if not email:
                # Apple hides email - generate placeholder
                email = f"{apple_id[:8]}@privaterelay.appleid.com"
            
            base_username = f"apple_user_{apple_id[:8]}"
            username = base_username
            
            user = User(
                email=email,
                username=username,
                apple_id=apple_id,
                friend_code=_generate_friend_code(),
            )
            db.add(user)
    
    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(user)
    
    return _create_token_response(user)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the currently authenticated user's profile.",
)
async def get_me(
    current_user: CurrentActiveUser,
) -> UserResponse:
    """Get the current authenticated user's profile.
    
    Args:
        current_user: The authenticated user.
        
    Returns:
        User profile data.
    """
    return UserResponse.model_validate(current_user)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request password reset",
    description="Send a password reset email to the user.",
)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: DatabaseSession,
) -> MessageResponse:
    """Request a password reset email.
    
    Note:
        Always returns success to prevent email enumeration.
        Implement actual email sending in production.
    
    Args:
        request: Email address for password reset.
        db: Database session.
        
    Returns:
        Success message (always, to prevent enumeration).
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if user and user.deleted_at is None:
        # Generate reset token
        reset_token = create_access_token(
            data={"sub": str(user.id), "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        
        # TODO: Send email with reset link
        # For now, just log it (in production, use a proper email service)
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Password reset token for {user.email}: {reset_token}")
    
    # Always return success to prevent email enumeration
    return MessageResponse(
        message="If an account exists with this email, a password reset link has been sent."
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password",
    description="Reset password using the token from email.",
)
async def reset_password(
    request: ResetPasswordRequest,
    db: DatabaseSession,
) -> MessageResponse:
    """Reset user password with a valid reset token.
    
    Args:
        request: Reset token and new password.
        db: Database session.
        
    Returns:
        Success message.
        
    Raises:
        HTTPException: 400 if token is invalid or expired.
    """
    from app.utils.security import verify_token
    from uuid import UUID
    
    payload = verify_token(request.token)
    
    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload",
        )
    
    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )
    
    # Validate new password
    password = request.new_password
    if not any(c.isupper() for c in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one uppercase letter",
        )
    if not any(c.islower() for c in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one lowercase letter",
        )
    if not any(c.isdigit() for c in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one digit",
        )
    
    # Update password
    user.password_hash = get_password_hash(request.new_password)
    await db.flush()
    
    return MessageResponse(message="Password has been reset successfully")
