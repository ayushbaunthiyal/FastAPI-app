import asyncio
from collections.abc import AsyncGenerator, Generator

import httpx
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.db import Base, get_db
from app.main import app

# Use a separate test database URL if desired, or override credentials
# For this example, we'll assume the environment (or .env.test) provides a valid TEST_DATABASE_URL
# In a real scenario, we might use a separate container or DB name.
# forcing the db url to use localhost if tests are running outside docker
TEST_DATABASE_URL = str(settings.DATABASE_URL).replace("db", "localhost")

engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
AsyncSessionLocalTest = async_sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def prepare_database() -> AsyncGenerator[None, None]:
    """
    Create tables before tests and drop them after.
    Requires a running DB.
    """
    try:
        async with engine_test.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with engine_test.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    except Exception as e:
        print(f"Skipping DB setup due to connection error: {e}")
        yield


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocalTest() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
