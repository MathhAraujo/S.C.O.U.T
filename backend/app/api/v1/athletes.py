import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.athlete import AthleteCreate, AthleteRead
from app.services import athletes as athlete_service

router = APIRouter(prefix="/athletes", tags=["athletes"])


@router.post("", response_model=AthleteRead, status_code=status.HTTP_201_CREATED)
async def create_athlete(
    payload: AthleteCreate,
    session: AsyncSession = Depends(get_session),
) -> AthleteRead:
    return await athlete_service.create_athlete(session, payload)


@router.get("", response_model=list[AthleteRead])
async def list_athletes(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[AthleteRead]:
    return await athlete_service.list_athletes(session, limit=limit, offset=offset)


@router.get("/{athlete_id}", response_model=AthleteRead)
async def get_athlete(
    athlete_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> AthleteRead:
    athlete = await athlete_service.get_athlete(session, athlete_id)
    if athlete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="athlete not found")
    return athlete
