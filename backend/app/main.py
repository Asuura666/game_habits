"""FastAPI main application."""
from app.logging_config import configure_logging
from app.middleware.logging_middleware import RequestLoggingMiddleware

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.database import close_db, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting {settings.app_name}...")
    yield
    # Shutdown
    print("Shutting down...")
    await close_db()



# Configure structured logging
configure_logging()
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Habit Tracker Gamifié - API Backend",
    docs_url="/api/docs" if settings.environment != "production" else None,
    redoc_url="/api/redoc" if settings.environment != "production" else None,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/api/metrics")


# Health check
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0",
        "environment": settings.environment,
    }


@app.get("/api/health/detailed", tags=["Health"])
async def health_detailed():
    """Detailed health check with DB and Redis status."""
    from redis import asyncio as aioredis
    from sqlalchemy import text

    db_status = "healthy"
    redis_status = "healthy"

    # Check database
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check Redis
    try:
        redis = aioredis.from_url(settings.redis_url)
        await redis.ping()
        await redis.close()
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" and redis_status == "healthy" else "unhealthy",
        "database": db_status,
        "redis": redis_status,
        "app": settings.app_name,
        "version": "1.0.0",
    }


# Import routers
from app.routers import auth as auth_module
from app.routers import admin
from app.routers import users as users_module
from app.routers import habits as habits_module
from app.routers import tasks as tasks_module
from app.routers import completions as completions_module
from app.routers import characters as characters_module
from app.routers import shop as shop_module
from app.routers import inventory as inventory_module
# from app.routers import combat as combat_module  # DISABLED
from app.routers import friends as friends_module
from app.routers import leaderboard as leaderboard_module
from app.routers import stats as stats_module
from app.routers import badges as badges_module

# Auth & Users
app.include_router(auth_module.router, prefix="/api")
app.include_router(users_module.router, prefix="/api")

# Core Features
app.include_router(habits_module.router, prefix="/api")
app.include_router(tasks_module.router, prefix="/api")
app.include_router(completions_module.router, prefix="/api")

# Gamification
app.include_router(characters_module.router, prefix="/api")
app.include_router(shop_module.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(inventory_module.router, prefix="/api")
# app.include_router(combat_module.router, prefix="/api")
app.include_router(badges_module.router, prefix="/api")

# Social
app.include_router(friends_module.router, prefix="/api")
app.include_router(leaderboard_module.router, prefix="/api")
app.include_router(stats_module.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
