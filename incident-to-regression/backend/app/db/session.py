"""SQLAlchemy async engine and session factory."""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return (or create) the shared async engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        kwargs: dict = {
            "echo": settings.DEBUG,
            "pool_pre_ping": True,
            "pool_recycle": settings.DB_POOL_RECYCLE,
        }
        if not settings.ASYNC_DATABASE_URL.startswith("sqlite"):
            kwargs["pool_size"] = settings.DB_POOL_SIZE
            kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
        _engine = create_async_engine(
            settings.ASYNC_DATABASE_URL,
            **kwargs,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return (or create) the shared session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _session_factory


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for database sessions with automatic rollback on error."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_database_connection() -> tuple[bool, float]:
    """Execute a minimal query to verify database connectivity.

    Returns:
        (success: bool, latency_ms: float)
    """
    start = time.monotonic()
    try:
        async with get_db_session() as session:
            await session.execute(text("SELECT 1"))
        latency_ms = (time.monotonic() - start) * 1000
        logger.debug("Database connection check passed", latency_ms=round(latency_ms, 2))
        return True, round(latency_ms, 2)
    except Exception as exc:
        latency_ms = (time.monotonic() - start) * 1000
        logger.warning(
            "Database connection check failed",
            error=str(exc),
            latency_ms=round(latency_ms, 2),
        )
        return False, round(latency_ms, 2)


async def close_engine() -> None:
    """Dispose the engine on application shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database engine disposed")
