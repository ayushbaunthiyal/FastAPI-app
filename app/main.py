import logging
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Starting up...")
    app.state.redis = await aioredis.from_url(str(settings.REDIS_URL))  # type: ignore[no-untyped-call]
    yield
    # Shutdown
    logger.info("Shutting down...")
    await app.state.redis.close()
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Request ID Middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


app.add_middleware(RequestIDMiddleware)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


@app.get("/health/live")
def health_live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
async def health_ready() -> dict[str, object]:
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
