import asyncio
import logging

from app.core.db import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init() -> None:
    async with AsyncSessionLocal():
        # Check if superuser exists
        # Note: We haven't implemented get_by_email yet in the script context,
        # so we'll just check directly or rely on unique constraint fail handling (naive)
        # For now, let's just log.
        logger.info("Creating initial data")

        # TODO: checking/creating superuser will be implemented in Phase 4 (Authentication)
        # when we have password hashing utilities.

        logger.info("Initial data created")


async def main() -> None:
    logger.info("Creating initial data")
    await init()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
