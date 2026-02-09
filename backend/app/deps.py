"""
Dependencies for FastAPI endpoints.
"""
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.database import get_db
from app.models.user import User

settings = get_settings()
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Validate JWT token and return the current user.
    
    Raises:
        HTTPException 401: If token is invalid or expired
        HTTPException 404: If user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(
        select(User)
        .options(selectinload(User.character))
        .where(User.id == UUID(user_id))
        .where(User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


async def get_current_user_with_character(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current user and ensure they have a character.
    
    Raises:
        HTTPException 400: If user has no character
    """
    if not current_user.character:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character required. Please complete onboarding first.",
        )
    return current_user


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserWithCharacter = Annotated[User, Depends(get_current_user_with_character)]
DBSession = Annotated[AsyncSession, Depends(get_db)]
