from typing import Callable, Optional

from fastapi import Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings


def _get_identifier(request: Request) -> str:
    user = getattr(request.state, "user", None)
    if user and hasattr(user, "id"):
        return f"user:{user.id}"
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(
    key_func=_get_identifier,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    enabled=settings.RATE_LIMIT_ENABLED,
    storage_uri=settings.REDIS_URL,
)


def rate_limit(
    limit: str,
    per: Optional[str] = None,
) -> Callable:
    if per:
        full = f"{limit}/{per}"
    else:
        full = limit
    return limiter.limit(full)


def auth_rate_limit() -> Callable:
    return limiter.limit(settings.RATE_LIMIT_AUTH)


def masking_rate_limit() -> Callable:
    return limiter.limit(settings.RATE_LIMIT_MASKING)


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    return Response(
        content='{"detail":"Rate limit exceeded. Please try again later."}',
        status_code=429,
        media_type="application/json",
    )
