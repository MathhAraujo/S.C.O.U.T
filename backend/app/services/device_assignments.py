import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.device_assignment import DeviceAssignment
from app.schemas.device_assignment import DeviceAssignmentCreate
from app.services.athletes import get_athlete
from app.services.devices import get_device_by_uid


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def get_active_assignment_for_device(
    session: AsyncSession,
    device_id: uuid.UUID,
) -> DeviceAssignment | None:
    result = await session.execute(
        select(DeviceAssignment)
        .where(DeviceAssignment.device_id == device_id, DeviceAssignment.ended_at.is_(None))
        .order_by(DeviceAssignment.started_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_device_assignment(
    session: AsyncSession,
    payload: DeviceAssignmentCreate,
) -> DeviceAssignment | None:
    device = await get_device_by_uid(session, payload.device_uid)
    athlete = await get_athlete(session, payload.athlete_id)
    if device is None or athlete is None:
        return None

    now = utcnow()
    active_assignment = await get_active_assignment_for_device(session, device.id)
    if active_assignment is not None:
        active_assignment.ended_at = now

    assignment = DeviceAssignment(
        device_id=device.id,
        athlete_id=athlete.id,
        started_at=now,
    )
    session.add(assignment)
    await session.commit()
    await session.refresh(assignment)
    return assignment


async def list_device_assignments(
    session: AsyncSession,
    *,
    device_uid: str | None,
    athlete_id: uuid.UUID | None,
    active_only: bool | None,
    limit: int,
    offset: int,
) -> list[DeviceAssignment]:
    statement = select(DeviceAssignment)

    if device_uid:
        statement = statement.join(Device, DeviceAssignment.device_id == Device.id).where(
            Device.device_uid == device_uid
        )

    if athlete_id:
        statement = statement.where(DeviceAssignment.athlete_id == athlete_id)

    if active_only:
        statement = statement.where(DeviceAssignment.ended_at.is_(None))

    statement = statement.order_by(DeviceAssignment.started_at.desc()).limit(limit).offset(offset)
    result = await session.execute(statement)
    return list(result.scalars().all())
