"""
Celery utilities for async database operations.

This module provides utilities for running async code in Celery tasks
without encountering event loop issues with asyncpg connection pools.
"""
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings


def run_async(coro):
    """
    Run an async coroutine in a sync Celery task context.
    
    Uses asyncio.run() which creates a new event loop, runs the coroutine,
    and closes the loop. This is safe for Celery workers.
    """
    return asyncio.run(coro)


@asynccontextmanager
async def get_celery_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for Celery tasks.
    
    This creates a new engine and session for each task invocation,
    avoiding the event loop mismatch issue where the global engine
    is bound to a different loop than the one used by the Celery worker.
    
    Usage:
        async with get_celery_db_session() as session:
            result = await session.execute(query)
            await session.commit()
    
    Yields:
        AsyncSession: A fresh database session
    """
    settings = get_settings()
    
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    
    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    try:
        async with session_maker() as session:
            yield session
    finally:
        await engine.dispose()
