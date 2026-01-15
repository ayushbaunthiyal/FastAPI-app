import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


async def init() -> None:
    try:
        engine = create_async_engine(str(settings.DATABASE_URL))

        for i in range(max_tries):
            try:
                msg = "Checking database connection..."
                logger.info(msg)

                async with engine.connect() as connection:
                    await connection.execute(select(1))

                msg = "Database connection proper."
                logger.info(msg)
                return
            except Exception as e:
                logger.warning(f"Connection attempt {i + 1} failed: {e}")
                await asyncio.sleep(wait_seconds)

        logger.error("Could not connect to database.")
        raise Exception("Database connection failed")
    except Exception as e:
        logger.error(e)
        raise e


if __name__ == "__main__":
    asyncio.run(init())
