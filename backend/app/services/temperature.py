import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.temperature_measurement import TemperatureMeasurement
from app.schemas.temperature import TemperaturePayload
from app.services.device_assignments import get_active_assignment_for_device
from app.services.devices import get_or_create_device


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def ingest_temperature(session: AsyncSession, payload: TemperaturePayload) -> uuid.UUID:
    device = await get_or_create_device(
        session,
        device_uid=payload.device_id,
        firmware_version=payload.firmware_version,
    )
    active_assignment = await get_active_assignment_for_device(session, device.id)
    received_at = utcnow()

    measurement = TemperatureMeasurement(
        device_id=device.id,
        athlete_id=active_assignment.athlete_id if active_assignment else None,
        sensor=payload.sensor,
        value_celsius=Decimal(str(payload.value_celsius)).quantize(Decimal("0.01")),
        unit=payload.unit,
        uptime_ms=payload.uptime_ms,
        measured_at=None,
        received_at=received_at,
    )
    session.add(measurement)
    await session.commit()
    await session.refresh(measurement)
    return measurement.id


async def list_temperature_measurements(
    session: AsyncSession,
    *,
    device_uid: str | None,
    athlete_id: uuid.UUID | None,
    start_date: datetime | None,
    end_date: datetime | None,
    limit: int,
    offset: int,
) -> list[TemperatureMeasurement]:
    statement = select(TemperatureMeasurement)

    if device_uid:
        statement = statement.join(Device, TemperatureMeasurement.device_id == Device.id).where(
            Device.device_uid == device_uid
        )

    if athlete_id:
        statement = statement.where(TemperatureMeasurement.athlete_id == athlete_id)

    if start_date:
        statement = statement.where(TemperatureMeasurement.received_at >= start_date)

    if end_date:
        statement = statement.where(TemperatureMeasurement.received_at <= end_date)

    statement = statement.order_by(TemperatureMeasurement.received_at.desc()).limit(limit).offset(offset)
    result = await session.execute(statement)
    return list(result.scalars().all())
