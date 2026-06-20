import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    device_uid: str = Field(..., min_length=1, max_length=255)
    firmware_version: str | None = Field(default=None, max_length=50)


class DeviceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    device_uid: str
    firmware_version: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
