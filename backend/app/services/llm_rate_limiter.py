"""
Redis-based rate limiter for LLM API calls.
Enforces daily limit per user to control costs.
"""
import time
from datetime import datetime, timezone
from typing import Optional

import structlog
from redis.asyncio import Redis

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class LLMRateLimiter:
    """
    Rate limiter for LLM API calls using Redis.
    
    Limits:
    - Per user: settings.llm_daily_limit requests per day (default: 20)
    - Global: 500 requests/day (cost protection)
    
    Uses calendar day (UTC midnight) for daily reset, not rolling 24h window.
    """
    
    def __init__(
        self,
        redis_url: str = None,
        daily_limit: int = None,
        global_daily_limit: int = 500,
    ):
        self.redis_url = redis_url or settings.redis_url
        self.daily_limit = daily_limit or settings.llm_daily_limit
        self.global_daily_limit = global_daily_limit
        self._redis: Optional[Redis] = None
    
    async def _get_redis(self) -> Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            self._redis = Redis.from_url(self.redis_url, decode_responses=True)
        return self._redis
    
    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    def _get_today_key(self) -> str:
        """Get today's date string for key prefix (UTC)."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    def _get_keys(self, user_id: str) -> tuple[str, str]:
        """Get Redis keys for rate limiting."""
        today = self._get_today_key()
        return (
            f"llm_rate:daily:{today}:user:{user_id}",
            f"llm_rate:daily:{today}:global",
        )
    
    def _seconds_until_midnight_utc(self) -> int:
        """Calculate seconds until UTC midnight."""
        now = datetime.now(timezone.utc)
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if tomorrow <= now:
            from datetime import timedelta
            tomorrow += timedelta(days=1)
        return int((tomorrow - now).total_seconds()) + 1
    
    async def check_rate_limit(self, user_id: str) -> tuple[bool, str]:
        """
        Check if user can make an LLM request.
        
        Args:
            user_id: User UUID string
            
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        redis = await self._get_redis()
        user_key, global_key = self._get_keys(user_id)
        
        # Get current counts
        pipe = redis.pipeline()
        pipe.get(user_key)
        pipe.get(global_key)
        results = await pipe.execute()
        
        user_count = int(results[0] or 0)
        global_count = int(results[1] or 0)
        
        log = logger.bind(
            user_id=user_id,
            user_count=user_count,
            global_count=global_count,
            daily_limit=self.daily_limit,
        )
        
        # Check global limit first
        if global_count >= self.global_daily_limit:
            log.warning("global_daily_rate_limit_exceeded")
            return False, "Service daily limit reached. Please try again tomorrow."
        
        # Check user daily limit
        if user_count >= self.daily_limit:
            log.warning("user_daily_rate_limit_exceeded")
            return False, f"Daily AI evaluation limit reached ({self.daily_limit}/day). Resets at midnight UTC."
        
        return True, "OK"
    
    async def record_request(self, user_id: str) -> None:
        """
        Record a successful LLM request.
        
        Args:
            user_id: User UUID string
        """
        redis = await self._get_redis()
        user_key, global_key = self._get_keys(user_id)
        
        # TTL until midnight UTC + buffer
        ttl = self._seconds_until_midnight_utc() + 60
        
        pipe = redis.pipeline()
        pipe.incr(user_key)
        pipe.expire(user_key, ttl)
        pipe.incr(global_key)
        pipe.expire(global_key, ttl)
        await pipe.execute()
        
        logger.debug("llm_request_recorded", user_id=user_id)
    
    async def get_remaining(self, user_id: str) -> dict:
        """
        Get remaining quota for a user.
        
        Args:
            user_id: User UUID string
            
        Returns:
            Dict with remaining requests info
        """
        redis = await self._get_redis()
        user_key, _ = self._get_keys(user_id)
        
        user_count = int(await redis.get(user_key) or 0)
        
        return {
            "requests_used_today": user_count,
            "requests_remaining_today": max(0, self.daily_limit - user_count),
            "daily_limit": self.daily_limit,
            "resets_at": "midnight UTC",
        }
    
    async def get_usage_count(self, user_id: str) -> int:
        """
        Get current usage count for a user today.
        
        Args:
            user_id: User UUID string
            
        Returns:
            Number of requests made today
        """
        redis = await self._get_redis()
        user_key, _ = self._get_keys(user_id)
        return int(await redis.get(user_key) or 0)


# Singleton
_rate_limiter: Optional[LLMRateLimiter] = None


def get_rate_limiter() -> LLMRateLimiter:
    """Get the rate limiter singleton."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = LLMRateLimiter()
    return _rate_limiter


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
