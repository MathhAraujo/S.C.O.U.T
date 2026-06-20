import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.device import DeviceCreate, DeviceRead
from app.services import devices as device_service

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
async def register_device(
    payload: DeviceCreate,
    session: AsyncSession = Depends(get_session),
) -> DeviceRead:
    return await device_service.register_device(session, payload)


@router.get("", response_model=list[DeviceRead])
async def list_devices(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[DeviceRead]:
    return await device_service.list_devices(session, limit=limit, offset=offset)


@router.get("/{device_id}", response_model=DeviceRead)
async def get_device(
    device_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> DeviceRead:
    device = await device_service.get_device(session, device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="device not found")
    return device
