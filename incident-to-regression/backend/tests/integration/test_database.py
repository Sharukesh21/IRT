"""Integration tests for database connectivity.

These tests require a running PostgreSQL instance.
They are skipped automatically when DATABASE_URL points to SQLite.

To run integration tests:
    DATABASE_URL=postgresql://user:pass@localhost/db pytest tests/integration/ -m integration
"""

import os
import pytest


def is_postgres_available() -> bool:
    """Check if the test database URL points to a real PostgreSQL instance."""
    url = os.environ.get("DATABASE_URL", "")
    return url.startswith("postgresql")


@pytest.mark.integration
@pytest.mark.skipif(
    not is_postgres_available(),
    reason="Integration tests require a running PostgreSQL instance (DATABASE_URL must point to postgresql://)",
)
async def test_database_connection_directly():
    """Verify direct database connectivity using check_database_connection."""
    from app.db.session import check_database_connection

    success, latency_ms = await check_database_connection()
    assert success is True, f"Database connection failed (latency: {latency_ms}ms)"
    assert latency_ms >= 0


@pytest.mark.integration
@pytest.mark.skipif(
    not is_postgres_available(),
    reason="Integration tests require a running PostgreSQL instance",
)
async def test_database_health_endpoint_returns_ok(client):
    """GET /api/v1/health/database must return 200 with a real PostgreSQL connection."""
    response = await client.get("/api/v1/health/database")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "postgresql"
    assert isinstance(data.get("latency_ms"), float)


@pytest.mark.integration
@pytest.mark.skipif(
    not is_postgres_available(),
    reason="Integration tests require a running PostgreSQL instance",
)
async def test_database_executes_simple_query(client):
    """Verify that a simple SQL query can be executed via the ORM session."""
    from sqlalchemy import text
    from app.db.session import get_db_session

    async with get_db_session() as session:
        result = await session.execute(text("SELECT 1 AS value"))
        row = result.fetchone()
        assert row is not None
        assert row[0] == 1
