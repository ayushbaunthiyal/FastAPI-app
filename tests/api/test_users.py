import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.user import UserCreate
from app.services.user_service import user_service


@pytest.mark.asyncio
async def test_create_user_open(client: AsyncClient, db_session: AsyncSession) -> None:
    email = "open_register@example.com"
    password = "password"
    data = {"email": email, "password": password, "full_name": "Open Register"}

    try:
        r = await client.post(f"{settings.API_V1_STR}/users/", json=data)
        assert r.status_code == 200
        new_user = r.json()
        assert new_user["email"] == email
        assert "id" in new_user
        assert "password" not in new_user
    except OSError:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_create_user_existing_email(client: AsyncClient, db_session: AsyncSession) -> None:
    email = "existing@example.com"
    password = "password"
    user_in = UserCreate(email=email, password=password, full_name="Existing User")

    try:
        await user_service.create_user(db_session, obj_in=user_in)

        data = {"email": email, "password": "newpassword", "full_name": "New Name"}
        r = await client.post(f"{settings.API_V1_STR}/users/", json=data)
        assert r.status_code == 400
    except OSError:
        pytest.skip("Database not available")
