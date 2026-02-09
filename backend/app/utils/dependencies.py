"""FastAPI dependencies for authentication and database access."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.models.user import User
from app.utils.security import verify_token

# Security scheme for Bearer token authentication
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncSession:
    """Dependency to get database session.
    
    Yields:
        AsyncSession: Database session that auto-commits on success
        and rolls back on exception.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Type alias for database dependency
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: DatabaseSession,
) -> User:
    """Get the current authenticated user from JWT token.
    
    Args:
        credentials: Bearer token from Authorization header.
        db: Database session.
        
    Returns:
        User: The authenticated user.
        
    Raises:
        HTTPException: 401 if token is missing, invalid, or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception
    
    # Query user from database
    result = await db.execute(
        select(User).where(User.id == user_uuid)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account has been deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get the current active user.
    
    Args:
        current_user: The authenticated user from get_current_user.
        
    Returns:
        User: The active authenticated user.
        
    Raises:
        HTTPException: 403 if user account is inactive/deleted.
    """
    if current_user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return current_user


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: DatabaseSession,
) -> User | None:
    """Optionally get the current user if authenticated.
    
    Unlike get_current_user, this doesn't raise if no token is provided.
    Useful for endpoints that work differently for authenticated vs anonymous users.
    
    Args:
        credentials: Bearer token from Authorization header.
        db: Database session.
        
    Returns:
        User if authenticated, None otherwise.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


async def require_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Require the current user to be an admin.
    
    Args:
        current_user: The authenticated active user.
        
    Returns:
        User: The admin user.
        
    Raises:
        HTTPException: 403 if user is not an admin.
        
    Note:
        Currently checks email domain. Implement proper role system later.
    """
    # TODO: Implement proper role-based access control
    # For now, check if user email matches admin pattern
    admin_emails = ["admin@habit-tracker.com", "moustafailane@gmail.com"]
    
    if current_user.email not in admin_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return current_user


# Type aliases for common dependency patterns
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
AdminUser = Annotated[User, Depends(require_admin)]
