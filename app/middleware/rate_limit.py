"""Rate limiting middleware using Redis."""
import time
from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware using Redis.

    Limits requests per IP address within a time window.
    """

    def __init__(
        self,
        app: object,
        requests_per_minute: int = 60,
        exclude_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.exclude_paths = exclude_paths or {"/health/live", "/health/ready"}

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"

        # Get Redis from app state
        redis = getattr(request.app.state, "redis", None)

        if redis:
            try:
                # Get current count
                current = await redis.get(key)
                current_count = int(current) if current else 0

                if current_count >= self.requests_per_minute:
                    # Calculate retry-after
                    ttl = await redis.ttl(key)
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": "Too many requests",
                            "retry_after": ttl if ttl > 0 else self.window_seconds,
                        },
                        headers={"Retry-After": str(ttl if ttl > 0 else self.window_seconds)},
                    )

                # Increment counter
                pipe = redis.pipeline()
                pipe.incr(key)
                if current_count == 0:
                    pipe.expire(key, self.window_seconds)
                await pipe.execute()

                # Add rate limit headers
                response = await call_next(request)
                response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
                response.headers["X-RateLimit-Remaining"] = str(
                    self.requests_per_minute - current_count - 1
                )
                return response

            except Exception:
                # If Redis fails, allow the request (fail open)
                pass

        return await call_next(request)
