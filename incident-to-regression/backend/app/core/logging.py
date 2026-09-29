"""Structured logging configuration using structlog."""

import logging
import sys
from contextvars import ContextVar

import structlog

from app.core.config import get_settings

# Context variable for request ID, propagated across async boundaries
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


def _add_request_id(
    logger: structlog.types.WrappedLogger,
    method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    """Inject request_id from context into every log record."""
    rid = request_id_ctx.get("")
    if rid:
        event_dict["request_id"] = rid
    return event_dict


def _add_service_name(
    logger: structlog.types.WrappedLogger,
    method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    """Inject service name into every log record."""
    event_dict["service"] = get_settings().APP_NAME
    return event_dict


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structlog for the application.

    Uses human-readable output in development and JSON in production.
    """
    settings = get_settings()
    is_production = settings.APP_ENV == "production"

    level = getattr(logging, log_level.upper(), logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        _add_service_name,
        _add_request_id,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if is_production:
        # JSON output for log aggregation (Loki, CloudWatch, etc.)
        processors: list[structlog.types.Processor] = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Pretty, colored output for development
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib logging to route through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger."""
    return structlog.get_logger(name)  # type: ignore[return-value]
