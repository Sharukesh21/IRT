"""In-memory rate limiter using sliding window algorithm.

No external dependencies required. Thread-safe for single-process deployments.
For multi-process or distributed setups, replace with Redis-backed limiter.
"""

import time
from collections import defaultdict, deque
from typing import Optional

from fastapi import HTTPException, Request

from app.core.config import get_settings


class InMemoryRateLimiter:
    """Sliding-window rate limiter backed by in-memory deques per client key."""

    def __init__(self, max_calls: int = 60, window_seconds: int = 60) -> None:
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._calls: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        """Return True if the request is within the rate limit, False otherwise."""
        now = time.time()
        dq = self._calls[key]
        cutoff = now - self.window_seconds
        # Evict expired timestamps
        while dq and dq[0] < cutoff:
            dq.popleft()
        if len(dq) >= self.max_calls:
            return False
        dq.append(now)
        return True

    def reset(self, key: str) -> None:
        """Clear rate-limit state for a key (useful in tests)."""
        self._calls.pop(key, None)


# Singleton — shared across all requests within the same process
_rate_limiter: Optional[InMemoryRateLimiter] = None


def get_rate_limiter() -> InMemoryRateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        settings = get_settings()
        _rate_limiter = InMemoryRateLimiter(
            max_calls=settings.RATE_LIMIT_PER_MINUTE,
            window_seconds=60,
        )
    return _rate_limiter


async def check_rate_limit(request: Request) -> None:
    """FastAPI dependency — raises HTTP 429 if the client exceeds the rate limit."""
    client_ip = request.client.host if request.client else "unknown"
    limiter = get_rate_limiter()
    if not limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please slow down and try again later.",
        )
