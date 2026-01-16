from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cached, invalidate_cache
from app.core.repository import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    @cached(prefix="user_email", ttl=300, exclude_kwargs=["db"], exclude_args_indices=[1])
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        result = await db.execute(select(User).filter(User.email == email, ~User.is_deleted))
        return result.scalars().first()

    @cached(prefix="user_id", ttl=300, exclude_kwargs=["db"], exclude_args_indices=[1])
    async def get(self, db: AsyncSession, id: Any) -> User | None:
        return await super().get(db, id)

    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: UserUpdate | dict[str, Any]
    ) -> User:
        user = await super().update(db=db, db_obj=db_obj, obj_in=obj_in)
        # Invalidate caches
        await invalidate_cache("user_email")
        await invalidate_cache("user_id")
        return user

    async def delete(self, db: AsyncSession, *, id: Any) -> User | None:
        user = await super().delete(db=db, id=id)
        if user:
            await invalidate_cache("user_email")
            await invalidate_cache("user_id")
        return user


user_repo = UserRepository(User)
