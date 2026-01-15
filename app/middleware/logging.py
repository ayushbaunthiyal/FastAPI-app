"""Request logging middleware."""
import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("app.access")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests with structured data."""

    # Paths to exclude from logging (e.g., health checks)
    EXCLUDE_PATHS = {"/health/live", "/health/ready", "/favicon.ico"}

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Skip logging for excluded paths
        if request.url.path in self.EXCLUDE_PATHS:
            return await call_next(request)

        start_time = time.perf_counter()
        request_id = getattr(request.state, "request_id", "-")

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.perf_counter() - start_time

        # Log structured data
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "client_ip": request.client.host if request.client else "-",
            },
        )

        # Log slow requests as warnings
        if duration > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} took {duration:.2f}s",
                extra={"request_id": request_id},
            )

        return response
