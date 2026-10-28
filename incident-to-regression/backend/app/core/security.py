"""Security, authentication, and rate-limiting middleware and dependencies."""

import time
from collections import defaultdict
from typing import Optional
from fastapi import Header, HTTPException, Request, Security, status
from fastapi.security.api_key import APIKeyHeader

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Simple in-memory sliding window rate limiter (for single-instance or baseline protection)
# Key: client_ip or api_key, Value: list of request timestamps
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


async def verify_api_key(
    request: Request,
    api_key: Optional[str] = Security(api_key_header),
) -> Optional[str]:
    """Verify incoming API key if API_KEY_ENABLED is true.
    
    Exempts documentation, metrics, and health check endpoints.
    """
    settings = get_settings()
    path = request.url.path

    # Public unauthenticated routes
    public_paths = [
        "/docs",
        "/redoc",
        "/openapi.json",
        f"{settings.API_PREFIX}/health",
        f"{settings.API_PREFIX}/health/live",
        f"{settings.API_PREFIX}/health/ready",
        f"{settings.API_PREFIX}/metrics",
    ]
    if any(path == p or path.startswith(f"{settings.API_PREFIX}/health") for p in public_paths):
        return None

    if not settings.API_KEY_ENABLED:
        return api_key

    if not api_key or api_key not in settings.API_KEYS:
        logger.warning("Unauthorized API request blocked", path=path, client=request.client.host if request.client else "unknown")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key. Provide a valid 'X-API-Key' header.",
        )
    return api_key


async def enforce_rate_limit(request: Request) -> None:
    """Enforce rate limits per minute based on client IP or API key."""
    settings = get_settings()
    now = time.time()
    one_minute_ago = now - 60.0

    client_id = request.headers.get("X-API-Key") or (request.client.host if request.client else "unknown")
    
    # Prune old timestamps
    timestamps = [t for t in _rate_limit_store[client_id] if t > one_minute_ago]
    
    if len(timestamps) >= settings.RATE_LIMIT_PER_MINUTE:
        logger.warning("Rate limit exceeded", client=client_id, limit=settings.RATE_LIMIT_PER_MINUTE)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please throttle your requests.",
        )

    timestamps.append(now)
    _rate_limit_store[client_id] = timestamps
