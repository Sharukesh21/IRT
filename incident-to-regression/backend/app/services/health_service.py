"""Health service — business logic for health check endpoints."""

from app.core.config import get_settings
from app.db.session import check_database_connection
from app.schemas.health import DatabaseHealthResponse, HealthResponse

APP_VERSION = "0.1.0"


class HealthService:
    """Provides health status information for the API and its dependencies."""

    async def get_system_health(self) -> HealthResponse:
        """Return the API service health status."""
        settings = get_settings()
        return HealthResponse(
            status="ok",
            service=settings.APP_NAME,
            environment=settings.APP_ENV,
            version=APP_VERSION,
        )

    async def get_database_health(self) -> DatabaseHealthResponse:
        """Check actual database connectivity and return status.

        This performs a real SELECT 1 query — it does NOT return a cached/fake status.
        """
        success, latency_ms = await check_database_connection()
        if success:
            return DatabaseHealthResponse(
                status="ok",
                database="postgresql",
                latency_ms=latency_ms,
            )
        return DatabaseHealthResponse(
            status="unavailable",
            database="postgresql",
            latency_ms=latency_ms,
            error="Unable to connect to PostgreSQL. Check database connectivity.",
        )


def get_health_service() -> HealthService:
    """Return a HealthService instance (dependency injection compatible)."""
    return HealthService()
