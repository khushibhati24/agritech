from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BuyerProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    business_name: str
    business_type: str
    address: str
    created_at: datetime


class BuyerProfileUpdate(BaseModel):
    business_name: str | None = None
    business_type: str | None = None
    address: str | None = None