import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate
from app.services.user_service import user_service


@pytest.mark.asyncio
async def test_create_user_service(db_session: AsyncSession) -> None:
    email = "service@example.com"
    password = "password"
    user_in = UserCreate(email=email, password=password)

    try:
        user = await user_service.create_user(db=db_session, obj_in=user_in)
        assert user.email == email
        assert hasattr(user, "id")
    except OSError:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_get_user_service(db_session: AsyncSession) -> None:
    email = "service_get@example.com"
    password = "password"
    user_in = UserCreate(email=email, password=password)

    try:
        await user_service.create_user(db=db_session, obj_in=user_in)
        user = await user_service.get_by_email(db_session, email=email)
        assert user is not None
        assert user.email == email
    except OSError:
        pytest.skip("Database not available")
