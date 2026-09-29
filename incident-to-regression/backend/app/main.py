"""FastAPI application entry point.

Creates and configures the FastAPI application with:
- Lifespan context (startup / shutdown events)
- CORS middleware
- Request ID middleware
- Structured logging
- Centralized exception handlers
- API router
"""

import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import configure_logging, get_logger, request_id_ctx
from app.db.session import close_engine

# Initialise settings eagerly to fail fast on misconfiguration
settings = get_settings()

# Configure logging before anything else
configure_logging(settings.LOG_LEVEL)
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Request ID Middleware
# ---------------------------------------------------------------------------


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns a unique request ID to every incoming request.

    - If the client provides X-Request-ID, that value is propagated.
    - Otherwise a new UUID4 is generated.
    - The ID is stored in a ContextVar (request_id_ctx) for use in logs.
    - The ID is included in the response as X-Request-ID.
    """

    async def dispatch(self, request: Request, call_next: object) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_ctx.set(request_id)
        try:
            response: Response = await call_next(request)  # type: ignore[operator]
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)


# ---------------------------------------------------------------------------
# Request Logging Middleware
# ---------------------------------------------------------------------------


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every request with timing and status."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        import time

        start = time.monotonic()
        response: Response = await call_next(request)  # type: ignore[operator]
        duration_ms = round((time.monotonic() - start) * 1000, 2)

        log_level = "warning" if response.status_code >= 400 else "info"
        getattr(logger, log_level)(
            "Request processed",
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response


# ---------------------------------------------------------------------------
# Security Headers Middleware
# ---------------------------------------------------------------------------


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that injects security headers."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        response: Response = await call_next(request)  # type: ignore[operator]
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        if str(request.url.path).startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
            
        return response


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle."""
    logger.info(
        "Starting application",
        name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="0.1.0",
    )
    yield
    logger.info("Shutting down application", name=settings.APP_NAME)
    await close_engine()


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Incident-to-Regression Platform API",
        description=(
            "Production-grade pipeline for converting online examination platform "
            "incidents into automated regression tests. "
            "\n\n"
            "## Architecture Components\n"
            "- **Foundation**: Monorepo structure, backend API, database layer, frontend dashboard, Docker environment, testing infrastructure, and CI pipeline.\n"
            "- **Simulator**: Exam simulator + event processing\n"
            "- **Incident Engine**: Incident engine + test generation\n"
            "- **Evaluation**: Test evaluation + benchmarking\n"
        ),
        version="1.0.0",
        contact={
            "name": "Incident-to-Regression Platform",
            "url": "http://localhost:5173",
        },
        license_info={
            "name": "MIT",
        },
        openapi_tags=[
            {
                "name": "Health",
                "description": "Service and dependency health checks.",
            },
            {
                "name": "Incidents",
                "description": "Incident capture and management.",
            },
            {
                "name": "Events",
                "description": "Event trace processing.",
            },
            {
                "name": "Regression Tests",
                "description": "Generated regression test management.",
            },
        ],
        lifespan=lifespan,
    )

    # CORS — must be first middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # Security Headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Request ID — before logging so logs include the ID
    app.add_middleware(RequestIDMiddleware)

    # Request logging
    app.add_middleware(RequestLoggingMiddleware)

    # Exception handlers
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # API routes
    app.include_router(api_router)

    return app


app = create_application()
