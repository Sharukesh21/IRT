"""Centralized exception handling and custom exception types."""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Custom exception hierarchy
# ---------------------------------------------------------------------------


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class ResourceNotFoundException(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Requested resource was not found") -> None:
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ValidationException(AppException):
    """Raised when business-level validation fails (distinct from schema validation)."""

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ConflictException(AppException):
    """Raised when an operation conflicts with current state."""

    def __init__(self, message: str = "Operation conflicts with current state") -> None:
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
        )


class DatabaseException(AppException):
    """Raised when a database operation fails."""

    def __init__(self, message: str = "Database operation failed") -> None:
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


# ---------------------------------------------------------------------------
# Error response builder
# ---------------------------------------------------------------------------


def _get_request_id(request: Request) -> str:
    """Extract request ID from request headers or state."""
    return str(request.headers.get("X-Request-ID", ""))


def _error_response(
    status_code: int,
    code: str,
    message: str,
    request_id: str,
) -> JSONResponse:
    """Build a standardised error JSON response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id,
            }
        },
    )


# ---------------------------------------------------------------------------
# FastAPI exception handlers
# ---------------------------------------------------------------------------


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle all custom application exceptions."""
    request_id = _get_request_id(request)
    logger.warning(
        "Application exception",
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
    )
    return _error_response(exc.status_code, exc.code, exc.message, request_id)


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle FastAPI/Starlette HTTP exceptions with consistent format."""
    request_id = _get_request_id(request)
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    message = str(exc.detail) if exc.detail else "An HTTP error occurred"
    return _error_response(exc.status_code, code, message, request_id)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic schema validation errors with consistent format."""
    request_id = _get_request_id(request)
    # Build a readable message from validation errors
    errors = exc.errors()
    messages = []
    for err in errors:
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "Validation error")
        messages.append(f"{loc}: {msg}" if loc else msg)
    message = "; ".join(messages) if messages else "Request validation failed"

    logger.info(
        "Validation error",
        path=request.url.path,
        errors=errors,
    )
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "SCHEMA_VALIDATION_ERROR",
        message,
        request_id,
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all handler for unexpected exceptions.

    Logs the full error internally but does NOT leak stack traces to clients.
    """
    request_id = _get_request_id(request)
    logger.exception(
        "Unhandled exception",
        path=request.url.path,
        exc_info=True,
    )
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "INTERNAL_SERVER_ERROR",
        "An unexpected error occurred. Please try again or contact support.",
        request_id,
    )
