from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    ProfileResponse,
    UserResponse,
    UserUpdate,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get(
    "/profile",
    response_model=ProfileResponse,
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await db.scalar(
        select(User)
        .where(User.id == current_user.id)
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    profile = None

    if user.role.value == "farmer":
        profile = user.farmer_profile

    elif user.role.value == "buyer":
        profile = user.buyer_profile

    elif user.role.value == "transporter":
        profile = user.transporter_profile

    profile_data = None

    if profile:
        profile_data = {
            column.name: getattr(profile, column.name)
            for column in profile.__table__.columns
            if column.name != "user_id"
        }

    return ProfileResponse(
        user=user,
        profile=profile_data,
    )


@router.put(
    "/update",
    response_model=UserResponse,
)
async def update_user(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.name is not None:
        current_user.name = data.name

    if data.phone is not None:
        current_user.phone = data.phone

    await db.commit()
    await db.refresh(current_user)

    return current_user