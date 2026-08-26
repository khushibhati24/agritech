from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    phone: str
    role: UserRole
    is_verified: bool
    created_at: datetime


class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None


class ProfileResponse(BaseModel):
    user: UserResponse
    profile: dict | None = None


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    phone: str
    role: UserRole
    is_verified: bool
    created_at: datetime