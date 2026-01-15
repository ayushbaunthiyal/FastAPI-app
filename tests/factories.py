"""Test data factories."""
import random
import string
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User


def random_string(length: int = 10) -> str:
    """Generate a random string."""
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_email() -> str:
    """Generate a random email."""
    return f"{random_string()}@{random_string()}.com"


async def create_user(
    db: AsyncSession,
    email: str | None = None,
    password: str = "password123",
    is_active: bool = True,
    is_superuser: bool = False,
) -> User:
    """Create a user in the database."""
    email = email or random_email()
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=random_string(),
        is_active=is_active,
        is_superuser=is_superuser,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
