from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        result = await db.execute(select(User).filter(User.email == email, ~User.is_deleted))
        return result.scalars().first()


user_repo = UserRepository(User)
