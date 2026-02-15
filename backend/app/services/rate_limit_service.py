"""
Rate Limit Service - Gestion des limites d'appels LLM.
"""
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.stats import RateLimit

if TYPE_CHECKING:
    from app.models.user import User

settings = get_settings()


async def check_llm_rate_limit(db: AsyncSession, user_id: UUID) -> tuple[bool, int, int]:
    """
    Check if user has exceeded LLM rate limit.
    
    Args:
        db: Database session
        user_id: User UUID
        
    Returns:
        Tuple of (is_allowed, remaining_calls, reset_in_seconds)
    """
    limit_type = "llm_evaluation"
    max_calls = settings.llm_daily_limit
    
    # Get or create rate limit record
    result = await db.execute(
        select(RateLimit).where(
            RateLimit.user_id == user_id,
            RateLimit.limit_type == limit_type
        )
    )
    rate_limit = result.scalar_one_or_none()
    
    now = datetime.now(timezone.utc)
    
    if rate_limit is None:
        # Create new rate limit record
        rate_limit = RateLimit(
            user_id=user_id,
            limit_type=limit_type,
            current_count=0,
            reset_at=now + timedelta(days=1)
        )
        db.add(rate_limit)
        await db.flush()
    
    # Check if reset is needed
    if rate_limit.reset_at <= now:
        rate_limit.current_count = 0
        rate_limit.reset_at = now + timedelta(days=1)
        await db.flush()
    
    # Check if limit exceeded
    remaining = max(0, max_calls - rate_limit.current_count)
    reset_in = int((rate_limit.reset_at - now).total_seconds())
    is_allowed = rate_limit.current_count < max_calls
    
    return is_allowed, remaining, reset_in


async def increment_llm_usage(db: AsyncSession, user_id: UUID) -> int:
    """
    Increment LLM usage counter.
    
    Args:
        db: Database session
        user_id: User UUID
        
    Returns:
        New count
    """
    limit_type = "llm_evaluation"
    
    result = await db.execute(
        select(RateLimit).where(
            RateLimit.user_id == user_id,
            RateLimit.limit_type == limit_type
        )
    )
    rate_limit = result.scalar_one_or_none()
    
    if rate_limit:
        rate_limit.current_count += 1
        await db.flush()
        return rate_limit.current_count
    
    return 0


async def get_llm_usage_stats(db: AsyncSession, user_id: UUID) -> dict:
    """
    Get LLM usage statistics for a user.
    
    Args:
        db: Database session
        user_id: User UUID
        
    Returns:
        Dict with usage stats
    """
    is_allowed, remaining, reset_in = await check_llm_rate_limit(db, user_id)
    
    return {
        "daily_limit": settings.llm_daily_limit,
        "remaining": remaining,
        "used": settings.llm_daily_limit - remaining,
        "reset_in_seconds": reset_in,
        "is_allowed": is_allowed,
    }
