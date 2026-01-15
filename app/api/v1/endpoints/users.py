from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
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
