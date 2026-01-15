"""FastAPI application entry point."""
import logging
import signal
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from redis import asyncio as aioredis
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.db import engine
from app.core.exceptions import register_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.timing import TimingMiddleware

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Graceful shutdown flag
shutdown_event = False


def handle_shutdown_signal(signum: int, frame: object) -> None:
    """Handle shutdown signals gracefully."""
    global shutdown_event
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event = True


# Register signal handlers (Unix only, will be no-op on Windows in Docker)
try:
    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    signal.signal(signal.SIGINT, handle_shutdown_signal)
except Exception:
    pass  # Signal handling may not work in all environments


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    logger.info("Starting up...")
    app.state.redis = await aioredis.from_url(str(settings.REDIS_URL))  # type: ignore[no-untyped-call]
    logger.info("Redis connection established")
    yield
    # Shutdown
    logger.info("Shutting down...")
    logger.info("Closing Redis connection...")
    await app.state.redis.close()
    logger.info("Disposing database engine...")
    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Register exception handlers
register_exception_handlers(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Request ID Middleware (must be first to set request_id for other middleware)
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# Add middleware (order matters - first added = last executed)
# So we add in reverse order of execution priority

# 1. Security headers (outermost - runs first on response)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Timing (tracks total response time)
app.add_middleware(TimingMiddleware)

# 3. Logging (logs request with timing info)
app.add_middleware(LoggingMiddleware)

# 4. Rate limiting
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# 5. Request ID (innermost - sets ID for all other middleware to use)
app.add_middleware(RequestIDMiddleware)

# 6. CORS (handled by FastAPI's built-in middleware)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


@app.get("/health/live")
def health_live() -> dict[str, str]:
    """Liveness probe - is the application running?"""
    return {"status": "ok"}


@app.get("/health/ready")
async def health_ready() -> dict[str, object]:
    """Readiness probe - is the application ready to serve traffic?"""
    # Check DB
    db_status = "ok"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"DB connection failed: {e}")
        db_status = "failed"

    # Check Redis
    redis_status = "ok"
    try:
        await app.state.redis.ping()
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        redis_status = "failed"

    status = "ok" if db_status == "ok" and redis_status == "ok" else "failed"
    return {"status": status, "details": {"database": db_status, "redis": redis_status}}
