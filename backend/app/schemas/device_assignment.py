import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviceAssignmentCreate(BaseModel):
    device_uid: str = Field(..., min_length=1, max_length=255)
    athlete_id: uuid.UUID


class DeviceAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    device_id: uuid.UUID
    athlete_id: uuid.UUID
    started_at: datetime
    ended_at: datetime | None
    created_at: datetime
    updated_at: datetime
