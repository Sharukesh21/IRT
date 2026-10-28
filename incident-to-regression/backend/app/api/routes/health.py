"""Health check API routes.

Provides two endpoints:
  GET /health        - Service liveness check
  GET /health/database - Real database connectivity check
"""

import time

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.schemas.health import DatabaseHealthResponse, HealthResponse
from app.services.health_service import get_health_service

router = APIRouter(prefix="/health", tags=["Health"])
logger = get_logger(__name__)


@router.get(
    "",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns the service status, name, environment, and version. "
    "Always returns 200 if the API process is running.",
)
async def health_check() -> HealthResponse:
    """Return API service health status."""
    service = get_health_service()
    return await service.get_system_health()


@router.get(
    "/live",
    summary="Liveness probe",
    description="Kubernetes liveness probe. Returns 200 if process is up.",
)
async def liveness_probe() -> dict[str, str]:
    return {"status": "alive"}


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Kubernetes readiness probe. Returns 200 only if DB and internal dependencies are ready.",
)
async def readiness_probe() -> JSONResponse:
    service = get_health_service()
    db_health = await service.get_database_health()
    if db_health.status == "ok":
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ready", "database": "ok", "latency_ms": db_health.latency_ms},
        )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "not_ready", "database": db_health.status, "error": db_health.error},
    )


@router.get(
    "/database",
    summary="Database connectivity check",
    description="Executes a SELECT 1 query against PostgreSQL to verify connectivity. "
    "Returns 503 if the database is unreachable.",
)
async def database_health_check() -> JSONResponse:
    """Return real-time database connectivity status.

    This endpoint ACTUALLY queries the database — it does not return a cached status.
    Use this to detect database outages from the frontend or monitoring systems.
    """
    service = get_health_service()
    result = await service.get_database_health()

    if result.status == "ok":
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result.model_dump(),
        )
    else:
        logger.warning("Database health check failed", status=result.status, error=result.error)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=result.model_dump(),
        )
