from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FarmerProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    address: str
    location: str
    farming_type: str
    created_at: datetime


class FarmerProfileUpdate(BaseModel):
    address: str | None = None
    location: str | None = None
    farming_type: str | None = None