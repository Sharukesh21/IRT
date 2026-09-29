"""Pytest configuration and shared fixtures.

Unit tests use an in-memory SQLite database (via aiosqlite) to avoid
requiring a running PostgreSQL instance.

Integration tests (marked with @pytest.mark.integration) use the
DATABASE_URL from environment, which must point to a real PostgreSQL instance.
"""

import os
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# MUST use a shared memory cache so threads can access the same DB in one test
TEST_DB_URL = "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true"
os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["ASYNC_DATABASE_URL"] = TEST_DB_URL
os.environ["APP_ENV"] = "test"
os.environ["LOG_LEVEL"] = "WARNING"

@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"

@pytest.fixture(scope="session")
async def engine():
    from app.db.base import Base
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()

@pytest.fixture
async def db(engine) -> AsyncSession:
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
        # Clean up data after each test instead of full drop for speed
        await session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()

@pytest.fixture(scope="session")
async def app():
    """Create a test FastAPI application instance."""
    from app.main import create_application
    return create_application()

@pytest.fixture
async def client(app, db):
    """Async HTTP client for testing FastAPI endpoints."""
    from app.db.session import get_db_session
    # Override dependency to return our test-scoped db
    app.dependency_overrides[get_db_session] = lambda: db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
