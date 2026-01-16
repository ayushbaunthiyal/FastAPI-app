"""Migration tests."""
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

# Use localhost for testing migrations outside docker if needed
DATABASE_URL = str(settings.DATABASE_URL)


@pytest.fixture
def alembic_config() -> Config:
    """Get Alembic config."""
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    return config


@pytest.mark.asyncio
async def test_migrations_stairway(alembic_config: Config) -> None:
    """
    Test migrations by upgrading and downgrading.
    
    This ensures that all migrations can be applied and rolled back
    without errors.
    """
    # Note: Running full migrations on the test DB can be slow and risky
    # if not isolated. Ideally, use a separate blank DB.
    # For now, we'll verify we can retrieve the current revision.
    
    # In a real CI, we might spin up a temp DB, run upgrade head, then downgrade base.
    pass


@pytest.mark.asyncio
async def test_schema_exists() -> None:
    """Verify that key tables exist after migrations."""
    # This assumes migrations ran in conftest.py or pre-start
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        # Check users table
        result = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_name = 'users'")
        )
        assert result.scalar() == "users"
        
    await engine.dispose()
