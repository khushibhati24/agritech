from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.db.session import get_db
from app.models.user import TransporterProfile, User
from app.schemas.transporter import (
    TransporterProfileResponse,
    TransporterProfileUpdate,
)


router = APIRouter(
    prefix="/transporters",
    tags=["Transporters"],
)


transporter_required = require_role(["transporter"])


@router.get(
    "/profile",
    response_model=TransporterProfileResponse,
)
async def get_transporter_profile(
    current_user: User = Depends(transporter_required),
    db: AsyncSession = Depends(get_db),
):
    profile = await db.scalar(
        select(TransporterProfile).where(
            TransporterProfile.user_id == current_user.id
        )
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Transporter profile not found",
        )

    return profile


@router.put(
    "/update",
    response_model=TransporterProfileResponse,
)
async def update_transporter_profile(
    data: TransporterProfileUpdate,
    current_user: User = Depends(transporter_required),
    db: AsyncSession = Depends(get_db),
):
    profile = await db.scalar(
        select(TransporterProfile).where(
            TransporterProfile.user_id == current_user.id
        )
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Transporter profile not found",
        )

    if data.vehicle_number is not None:
        profile.vehicle_number = data.vehicle_number

    if data.vehicles_type is not None:
        profile.vehicles_type = data.vehicles_type

    if data.capacity is not None:
        profile.capacity = data.capacity

    await db.commit()
    await db.refresh(profile)

    return profile