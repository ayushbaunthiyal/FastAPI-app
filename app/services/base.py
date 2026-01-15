from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.models.base import BaseModel as DBModel

ModelType = TypeVar("ModelType", bound=DBModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService[ModelType, CreateSchemaType, UpdateSchemaType]:
    def __init__(self, repository: BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
        self.repository = repository

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        return await self.repository.get(db, id)

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return await self.repository.get_multi(db, skip=skip, limit=limit)

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        return await self.repository.create(db, obj_in=obj_in)

    async def update(self, db: AsyncSession, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        return await self.repository.update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: Any) -> ModelType | None:
        return await self.repository.delete(db, id=id)
