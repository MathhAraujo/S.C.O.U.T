import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.schemas.device import DeviceCreate


async def get_device(session: AsyncSession, device_id: uuid.UUID) -> Device | None:
    return await session.get(Device, device_id)


async def get_device_by_uid(session: AsyncSession, device_uid: str) -> Device | None:
    result = await session.execute(select(Device).where(Device.device_uid == device_uid))
    return result.scalar_one_or_none()


async def get_or_create_device(
    session: AsyncSession,
    device_uid: str,
    firmware_version: str | None = None,
) -> Device:
    device = await get_device_by_uid(session, device_uid)
    if device is not None:
        if firmware_version and device.firmware_version != firmware_version:
            device.firmware_version = firmware_version
        return device

    device = Device(device_uid=device_uid, firmware_version=firmware_version)
    session.add(device)
    await session.flush()
    return device


async def register_device(session: AsyncSession, payload: DeviceCreate) -> Device:
    device = await get_device_by_uid(session, payload.device_uid)
    if device is not None:
        return device

    device = Device(**payload.model_dump())
    session.add(device)
    await session.commit()
    await session.refresh(device)
    return device


async def list_devices(session: AsyncSession, *, limit: int, offset: int) -> list[Device]:
    result = await session.execute(select(Device).order_by(Device.created_at.desc()).limit(limit).offset(offset))
    return list(result.scalars().all())
