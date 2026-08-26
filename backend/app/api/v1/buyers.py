from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.db.session import get_db
from app.models.user import BuyerProfile, User
from app.schemas.buyer import (
    BuyerProfileResponse,
    BuyerProfileUpdate,
)


router = APIRouter(
    prefix="/buyers",
    tags=["Buyers"],
)


buyer_required = require_role(["buyer"])


@router.get(
    "/profile",
    response_model=BuyerProfileResponse,
)
async def get_buyer_profile(
    current_user: User = Depends(buyer_required),
    db: AsyncSession = Depends(get_db),
):
    profile = await db.scalar(
        select(BuyerProfile).where(
            BuyerProfile.user_id == current_user.id
        )
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Buyer profile not found",
        )

    return profile


@router.put(
    "/update",
    response_model=BuyerProfileResponse,
)
async def update_buyer_profile(
    data: BuyerProfileUpdate,
    current_user: User = Depends(buyer_required),
    db: AsyncSession = Depends(get_db),
):
    profile = await db.scalar(
        select(BuyerProfile).where(
            BuyerProfile.user_id == current_user.id
        )
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Buyer profile not found",
        )

    if data.business_name is not None:
        profile.business_name = data.business_name

    if data.business_type is not None:
        profile.business_type = data.business_type

    if data.address is not None:
        profile.address = data.address

    await db.commit()
    await db.refresh(profile)

    return profile