"""
Pre-start script that runs before the main application.
Ensures database is ready, migrations are applied, and initial data exists.
"""
import asyncio
import logging

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


async def check_db_connection() -> None:
    """Wait for database to be ready."""
    engine = create_async_engine(str(settings.DATABASE_URL))

    for i in range(max_tries):
        try:
            logger.info("Checking database connection...")
            async with engine.connect() as connection:
                await connection.execute(select(1))
            logger.info("Database connection successful.")
            await engine.dispose()
            return
        except Exception as e:
            logger.warning(f"Connection attempt {i + 1} failed: {e}")
            await asyncio.sleep(wait_seconds)

    raise Exception("Could not connect to database after maximum retries.")


def run_migrations() -> None:
    """Run Alembic migrations to ensure schema is up to date."""
    import subprocess

    logger.info("Running database migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error(f"Migration failed: {result.stderr}")
        raise Exception(f"Migration failed: {result.stderr}")
    logger.info("Migrations completed successfully.")
    if result.stdout:
        logger.info(result.stdout)


async def create_initial_data() -> None:
    """Create initial data if it doesn't exist."""
    from app.core.db import AsyncSessionLocal
    from app.models.user import User
    from app.repositories.user import UserRepository
    from app.schemas.user import UserCreate
    from app.core.security import get_password_hash

    logger.info("Checking for initial data...")

    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)

        # Check if any superuser exists
        result = await session.execute(
            select(User).where(User.is_superuser == True).limit(1)  # noqa: E712
        )
        superuser = result.scalar_one_or_none()

        if not superuser:
            logger.info("Creating initial superuser...")
            # Create default superuser
            superuser_data = UserCreate(
                email="admin@example.com",
                password="admin123",  # Change this in production!
                full_name="System Administrator",
            )
            hashed_password = get_password_hash(superuser_data.password)

            new_user = User(
                email=superuser_data.email,
                hashed_password=hashed_password,
                full_name=superuser_data.full_name,
                is_active=True,
                is_superuser=True,
            )
            session.add(new_user)
            await session.commit()
            logger.info(f"Superuser created: {superuser_data.email}")
        else:
            logger.info("Superuser already exists, skipping creation.")


async def main() -> None:
    """Main prestart sequence."""
    logger.info("=" * 50)
    logger.info("Starting pre-start initialization...")
    logger.info("=" * 50)

    # Step 1: Wait for database
    await check_db_connection()

    # Step 2: Run migrations
    run_migrations()

    # Step 3: Create initial data
    await create_initial_data()

    logger.info("=" * 50)
    logger.info("Pre-start initialization complete!")
    logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
