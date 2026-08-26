from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.db.session import get_db
from app.models.user import AdminLog, User, UserRole
from app.schemas.admin import (
    AdminReportsResponse,
    AdminUsersResponse,
    RoleCount,
    VerifyUserRequest,
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


admin_required = require_role(["admin"])


@router.get(
    "/users",
    response_model=AdminUsersResponse,
)
async def list_users(
    role: UserRole | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
):
    query = select(User)

    if role:
        query = query.where(User.role == role)

    total = await db.scalar(
        select(func.count()).select_from(query.subquery())
    )

    query = (
        query
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.scalars(query)
    users = result.all()

    return AdminUsersResponse(
        total=total or 0,
        page=page,
        page_size=page_size,
        users=users,
    )


@router.post("/verify")
async def verify_user(
    data: VerifyUserRequest,
    current_user: User = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
):
    user = await db.scalar(
        select(User).where(User.id == data.user_id)
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.is_verified:
        return {
            "success": True,
            "message": "User is already verified",
        }

    user.is_verified = True

    db.add(
        AdminLog(
            admin_id=current_user.id,
            action="verify_user",
            details={
                "user_id": str(user.id),
                "email": user.email,
            },
        )
    )

    await db.commit()

    return {
        "success": True,
        "message": "User verified successfully",
    }


@router.get(
    "/reports",
    response_model=AdminReportsResponse,
)
async def reports(
    current_user: User = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
):
    total_users = await db.scalar(
        select(func.count(User.id))
    )

    verification_queue = await db.scalar(
        select(func.count(User.id)).where(
            User.is_verified.is_(False)
        )
    )

    role_counts = await db.execute(
        select(
            User.role,
            func.count(User.id),
        )
        .group_by(User.role)
    )

    breakdown = [
        RoleCount(
            role=role,
            count=count,
        )
        for role, count in role_counts.all()
    ]

    return AdminReportsResponse(
        total_users=total_users or 0,
        verification_queue=verification_queue or 0,
        breakdown=breakdown,
    )