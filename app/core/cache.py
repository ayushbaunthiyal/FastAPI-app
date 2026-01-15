"""Redis caching utilities."""
import functools
import hashlib
import json
import logging
from typing import Any, Callable, TypeVar

from redis import asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class RedisCache:
    """Redis cache client wrapper."""

    def __init__(self) -> None:
        self._client: aioredis.Redis | None = None

    async def connect(self) -> aioredis.Redis:
        """Connect to Redis."""
        if self._client is None:
            self._client = await aioredis.from_url(
                str(settings.REDIS_URL),
                encoding="utf-8",
                decode_responses=True,
            )  # type: ignore[no-untyped-call]
        return self._client

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> aioredis.Redis:
        """Get Redis client."""
        if self._client is None:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._client

    async def get(self, key: str) -> str | None:
        """Get value from cache."""
        return await self.client.get(key)

    async def set(
        self, key: str, value: str, ttl: int | None = None
    ) -> None:
        """Set value in cache with optional TTL."""
        if ttl:
            await self.client.setex(key, ttl, value)
        else:
            await self.client.set(key, value)

    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        await self.client.delete(key)

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        keys = await self.client.keys(pattern)
        if keys:
            return await self.client.delete(*keys)
        return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return bool(await self.client.exists(key))


# Global cache instance
cache = RedisCache()


def make_cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    """Generate a cache key from arguments."""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_data.encode()).hexdigest()[:16]
    return f"{prefix}:{key_hash}"


def cached(prefix: str, ttl: int = 300, exclude_kwargs: list[str] | None = None) -> Callable[[F], F]:
    """
    Decorator to cache function results in Redis.

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (default: 5 minutes)
        exclude_kwargs: List of keyword argument names to exclude from cache key
    """
    exclude = set(exclude_kwargs or [])

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Skip first arg if it's likely self/cls
            cache_args = args[1:] if args else args
            
            # Filter excluded kwargs (like db session)
            cache_kwargs = {k: v for k, v in kwargs.items() if k not in exclude}

            key = make_cache_key(prefix, *cache_args, **cache_kwargs)

            try:
                # Try to get from cache
                cached_value = await cache.get(key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {key}")
                    return json.loads(cached_value)
            except Exception as e:
                logger.warning(f"Cache get error: {e}")

            # Execute function
            result = await func(*args, **kwargs)

            try:
                # Store in cache
                await cache.set(key, json.dumps(result, default=str), ttl)
                logger.debug(f"Cache set: {key}")
            except Exception as e:
                logger.warning(f"Cache set error: {e}")

            return result

        return wrapper  # type: ignore[return-value]

    return decorator


async def invalidate_cache(prefix: str) -> int:
    """Invalidate all cache entries with given prefix."""
    return await cache.delete_pattern(f"{prefix}:*")
