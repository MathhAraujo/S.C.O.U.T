import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.temperature import (
    TemperatureIngestResponse,
    TemperatureMeasurementRead,
    TemperaturePayload,
)
from app.services import temperature as temperature_service

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post("/temperature", response_model=TemperatureIngestResponse)
async def ingest_temperature(
    payload: TemperaturePayload,
    session: AsyncSession = Depends(get_session),
) -> TemperatureIngestResponse:
    measurement_id = await temperature_service.ingest_temperature(session, payload)
    return TemperatureIngestResponse(
        message="temperature measurement registered",
        measurement_id=measurement_id,
    )


@router.get("/temperature", response_model=list[TemperatureMeasurementRead])
async def list_temperature_measurements(
    device_uid: str | None = Query(default=None),
    athlete_id: uuid.UUID | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[TemperatureMeasurementRead]:
    return await temperature_service.list_temperature_measurements(
        session,
        device_uid=device_uid,
        athlete_id=athlete_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
