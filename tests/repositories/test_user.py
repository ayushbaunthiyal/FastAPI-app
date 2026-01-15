import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import user_repo
from app.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession) -> None:
    # This test will fail if DB is not reachable, but code structure is valid
    email = "test@example.com"
    password = "password"

    # We need a schema for creation, but for now we are using the model directly
    # or a dict as the repo accepts generic inputs in the base implementation
    # The Generic Type in user_repo is defined with Placeholders, so we mock the input behavior.

    try:
        user = await user_repo.create(
            db_session,
            obj_in={
                "email": email,
                "hashed_password": "hashed_password_mock",
                "full_name": "Test User",
                "is_active": True,
                "is_superuser": False,
            },
        )
        assert user.email == email
        assert hasattr(user, "id")
    except OSError:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession) -> None:
    email = "get@example.com"

    try:
        await user_repo.create(
            db_session,
            obj_in={
                "email": email,
                "hashed_password": "hashed_password_mock",
                "full_name": "User",
            },
        )
        user = await user_repo.get_by_email(db_session, email=email)
        assert user is not None
        assert user.email == email
    except OSError:
        pytest.skip("Database not available")
