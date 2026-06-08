import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TemperaturePayload(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=255)
    sensor: Literal["MAX30205"]
    value_celsius: float
    unit: Literal["celsius"]
    firmware_version: str | None = Field(default=None, max_length=50)
    uptime_ms: int | None = Field(default=None, ge=0)


class TemperatureIngestResponse(BaseModel):
    message: str
    measurement_id: uuid.UUID


class TemperatureMeasurementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    device_id: uuid.UUID
    athlete_id: uuid.UUID | None
    sensor: str
    value_celsius: float
    unit: str
    uptime_ms: int | None
    measured_at: datetime | None
    received_at: datetime
    created_at: datetime
