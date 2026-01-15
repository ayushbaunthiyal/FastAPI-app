from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.repositories.user import UserRepository, user_repo
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
        self.repository: UserRepository = repository

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        return await self.repository.get_by_email(db, email=email)

    async def create_user(self, db: AsyncSession, obj_in: UserCreate) -> User:
        obj_in.password = get_password_hash(obj_in.password)
        return await self.create(db, obj_in=obj_in)

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> User | None:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


user_service = UserService(user_repo)
