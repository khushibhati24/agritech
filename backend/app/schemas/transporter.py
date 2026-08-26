from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TransporterProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    vehicle_number: str
    vehicles_type: str
    capacity: str
    created_at: datetime


class TransporterProfileUpdate(BaseModel):
    vehicle_number: str | None = None
    vehicles_type: str | None = None
    capacity: str | None = None