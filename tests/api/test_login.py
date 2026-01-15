from datetime import timedelta
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.schemas.user import UserCreate
from app.services.user_service import user_service


@pytest.mark.asyncio
async def test_get_access_token(client: AsyncClient, db_session: AsyncSession) -> None:
    email = "login@example.com"
    password = "password"
    user_in = UserCreate(email=email, password=password, full_name="Test Login")
    try:
        await user_service.create_user(db_session, obj_in=user_in)
        login_data = {
            "username": email,
            "password": password,
        }
        r = await client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        assert r.status_code == 200
        assert "access_token" in tokens
        assert tokens["access_token"]
    except OSError:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_use_access_token(client: AsyncClient, db_session: AsyncSession, event_loop: Any) -> None:
    email = "token@example.com"
    password = "password"
    user_in = UserCreate(email=email, password=password, full_name="Test Token")
    try:
        user = await user_service.create_user(db_session, obj_in=user_in)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(user.id, expires_delta=access_token_expires)

        # TODO: Once we have a protected endpoint, verify using it.
        # For now, we verify the token is valid manually
        payload = security.jwt.decode(access_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        assert payload["sub"] == str(user.id)
    except OSError:
        pytest.skip("Database not available")
