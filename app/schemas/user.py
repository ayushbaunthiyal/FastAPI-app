from pydantic import EmailStr

from app.schemas.base import ORMModel


# Shared properties
class UserBase(ORMModel):
    email: EmailStr | None = None
    is_active: bool | None = True
    is_superuser: bool = False
    full_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: str | None = None


# Properties to return via API
class UserResponse(UserBase):
    id: int
