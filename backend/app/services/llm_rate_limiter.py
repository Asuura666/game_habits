"""
Redis-based rate limiter for LLM API calls.
Prevents abuse and controls costs.
"""
import time
from typing import Optional

import structlog
from redis.asyncio import Redis

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# Default limits
DEFAULT_REQUESTS_PER_HOUR = 20
DEFAULT_REQUESTS_PER_MINUTE = 5


class LLMRateLimiter:
    """
    Rate limiter for LLM API calls using Redis sliding window.
    
    Limits:
    - Per user: 20 requests/hour, 5 requests/minute
    - Global: 200 requests/hour (cost protection)
    """
    
    def __init__(
        self,
        redis_url: str = None,
        requests_per_hour: int = DEFAULT_REQUESTS_PER_HOUR,
        requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE,
        global_requests_per_hour: int = 200,
    ):
        self.redis_url = redis_url or settings.redis_url
        self.requests_per_hour = requests_per_hour
        self.requests_per_minute = requests_per_minute
        self.global_requests_per_hour = global_requests_per_hour
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
    
    def _get_keys(self, user_id: str) -> tuple[str, str, str]:
        """Get Redis keys for rate limiting."""
        return (
            f"llm_rate:user:{user_id}:hour",
            f"llm_rate:user:{user_id}:minute",
            f"llm_rate:global:hour",
        )
    
    async def check_rate_limit(self, user_id: str) -> tuple[bool, str]:
        """
        Check if user can make an LLM request.
        
        Args:
            user_id: User UUID string
            
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        redis = await self._get_redis()
        now = int(time.time())
        
        hour_key, minute_key, global_key = self._get_keys(user_id)
        
        # Clean old entries and count current
        hour_window_start = now - 3600
        minute_window_start = now - 60
        
        pipe = redis.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(hour_key, 0, hour_window_start)
        pipe.zremrangebyscore(minute_key, 0, minute_window_start)
        pipe.zremrangebyscore(global_key, 0, hour_window_start)
        
        # Count current
        pipe.zcard(hour_key)
        pipe.zcard(minute_key)
        pipe.zcard(global_key)
        
        results = await pipe.execute()
        hour_count = results[3]
        minute_count = results[4]
        global_count = results[5]
        
        log = logger.bind(
            user_id=user_id,
            hour_count=hour_count,
            minute_count=minute_count,
            global_count=global_count,
        )
        
        # Check limits
        if global_count >= self.global_requests_per_hour:
            log.warning("global_rate_limit_exceeded")
            return False, "Service temporarily busy. Please try again later."
        
        if hour_count >= self.requests_per_hour:
            log.warning("user_hourly_rate_limit_exceeded")
            return False, f"Hourly limit reached ({self.requests_per_hour}/hour). Resets in {60 - (now % 3600) // 60} minutes."
        
        if minute_count >= self.requests_per_minute:
            log.warning("user_minute_rate_limit_exceeded")
            return False, f"Too many requests. Please wait {60 - (now % 60)} seconds."
        
        return True, "OK"
    
    async def record_request(self, user_id: str) -> None:
        """
        Record a successful LLM request.
        
        Args:
            user_id: User UUID string
        """
        redis = await self._get_redis()
        now = int(time.time())
        
        hour_key, minute_key, global_key = self._get_keys(user_id)
        
        pipe = redis.pipeline()
        
        # Add to sorted sets with timestamp as score
        pipe.zadd(hour_key, {f"{now}:{id(now)}": now})
        pipe.zadd(minute_key, {f"{now}:{id(now)}": now})
        pipe.zadd(global_key, {f"{now}:{user_id}": now})
        
        # Set expiry (cleanup)
        pipe.expire(hour_key, 3700)  # 1 hour + buffer
        pipe.expire(minute_key, 120)  # 2 minutes
        pipe.expire(global_key, 3700)
        
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
        now = int(time.time())
        
        hour_key, minute_key, _ = self._get_keys(user_id)
        
        hour_window_start = now - 3600
        minute_window_start = now - 60
        
        pipe = redis.pipeline()
        pipe.zcount(hour_key, hour_window_start, now)
        pipe.zcount(minute_key, minute_window_start, now)
        results = await pipe.execute()
        
        return {
            "requests_remaining_hour": max(0, self.requests_per_hour - results[0]),
            "requests_remaining_minute": max(0, self.requests_per_minute - results[1]),
            "limit_per_hour": self.requests_per_hour,
            "limit_per_minute": self.requests_per_minute,
        }


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
