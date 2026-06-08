import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class AthleteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    birth_date: date | None = None
    position: str | None = Field(default=None, max_length=100)
    team: str | None = Field(default=None, max_length=100)


class AthleteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    birth_date: date | None
    position: str | None
    team: str | None
    created_at: datetime
    updated_at: datetime
