from uuid import UUID

from pydantic import BaseModel, Field

from app.models.user import UserRole
from app.schemas.user import AdminUserResponse


class VerifyUserRequest(BaseModel):
    user_id: UUID


class AdminUsersResponse(BaseModel):
    success: bool = True
    total: int
    page: int
    page_size: int
    users: list[AdminUserResponse]


class RoleCount(BaseModel):
    role: UserRole
    count: int


class AdminReportsResponse(BaseModel):
    success: bool = True
    total_users: int
    verification_queue: int
    breakdown: list[RoleCount]