"""
Health Check Router

Provides endpoints for monitoring service health:
- /api/health: Simple liveness check
- /api/health/detailed: Full system health including DB and Redis
"""

from datetime import datetime, timezone
from typing import Any, Dict

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter()


class HealthResponse(BaseModel):
    """Basic health check response."""
    status: str
    timestamp: str
    version: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response with component status."""
    status: str
    timestamp: str
    version: str
    environment: str
    components: Dict[str, Any]


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Simple liveness check for the API",
)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.
    
    Returns:
        HealthResponse: Status, timestamp, and version
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=settings.app_version,
    )


@router.get(
    "/health/detailed",
    response_model=DetailedHealthResponse,
    summary="Detailed Health Check",
    description="Full system health including database and Redis connectivity",
)
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
) -> DetailedHealthResponse:
    """
    Detailed health check with component status.
    
    Checks:
    - Database connectivity
    - Redis connectivity (via Celery broker)
    
    Returns:
        DetailedHealthResponse: Full health status with component details
    
    Raises:
        HTTPException: If any critical component is unhealthy
    """
    components: Dict[str, Any] = {}
    overall_healthy = True
    
    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        components["database"] = {
            "status": "healthy",
            "type": "postgresql",
        }
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        components["database"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        overall_healthy = False
    
    # Check Redis (basic connectivity)
    try:
        import redis.asyncio as redis
        
        redis_client = redis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.close()
        components["redis"] = {
            "status": "healthy",
            "type": "redis",
        }
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        components["redis"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        overall_healthy = False
    
    response = DetailedHealthResponse(
        status="healthy" if overall_healthy else "degraded",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=settings.app_version,
        environment=settings.environment,
        components=components,
    )
    
    if not overall_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response.model_dump(),
        )
    
    return response
