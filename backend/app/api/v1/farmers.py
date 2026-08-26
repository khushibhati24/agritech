from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.db.session import get_db
from app.models.user import FarmerProfile, User
from app.schemas.farmer import (
    FarmerProfileResponse,
    FarmerProfileUpdate,
)


router = APIRouter(
    prefix="/farmers",
    tags=["Farmers"],
)


farmer_required = require_role(["farmer"])


@router.get(
    "/profile",
    response_model=FarmerProfileResponse,
)
async def get_farmer_profile(
    current_user: User = Depends(farmer_required),
    db: AsyncSession = Depends(get_db),
):
    profile = await db.scalar(
        select(FarmerProfile).where(
            FarmerProfile.user_id == current_user.id
        )
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Farmer profile not found",
        )

    return profile


@router.put(
    "/update",
    response_model=FarmerProfileResponse,
)
async def update_farmer_profile(
    data: FarmerProfileUpdate,
    current_user: User = Depends(farmer_required),
    db: AsyncSession = Depends(get_db),
):
    profile = await db.scalar(
        select(FarmerProfile).where(
            FarmerProfile.user_id == current_user.id
        )
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Farmer profile not found",
        )

    if data.address is not None:
        profile.address = data.address

    if data.location is not None:
        profile.location = data.location

    if data.farming_type is not None:
        profile.farming_type = data.farming_type

    await db.commit()
    await db.refresh(profile)

    return profile