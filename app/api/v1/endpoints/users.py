from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.cache import cached
from app.core.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import user_service

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user_open(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = await user_service.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = await user_service.create_user(db, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=UserResponse)
@cached(prefix="user", ttl=60, exclude_kwargs=["db", "current_user"])
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> UserResponse:
    """
    Get a specific user by id.
    """
    user = await user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User with this ID not found")
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return UserResponse.model_validate(user)
