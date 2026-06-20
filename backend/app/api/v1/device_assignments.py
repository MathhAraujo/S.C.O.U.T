import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.device_assignment import DeviceAssignmentCreate, DeviceAssignmentRead
from app.services import device_assignments as assignment_service

router = APIRouter(prefix="/device-assignments", tags=["device assignments"])


@router.post("", response_model=DeviceAssignmentRead, status_code=status.HTTP_201_CREATED)
async def create_device_assignment(
    payload: DeviceAssignmentCreate,
    session: AsyncSession = Depends(get_session),
) -> DeviceAssignmentRead:
    assignment = await assignment_service.create_device_assignment(session, payload)
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="device or athlete not found",
        )
    return assignment


@router.get("", response_model=list[DeviceAssignmentRead])
async def list_device_assignments(
    device_uid: str | None = Query(default=None),
    athlete_id: uuid.UUID | None = Query(default=None),
    active_only: bool | None = Query(default=None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[DeviceAssignmentRead]:
    return await assignment_service.list_device_assignments(
        session,
        device_uid=device_uid,
        athlete_id=athlete_id,
        active_only=active_only,
        limit=limit,
        offset=offset,
    )
