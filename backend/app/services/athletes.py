import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.athlete import Athlete
from app.schemas.athlete import AthleteCreate


async def create_athlete(session: AsyncSession, payload: AthleteCreate) -> Athlete:
    athlete = Athlete(**payload.model_dump())
    session.add(athlete)
    await session.commit()
    await session.refresh(athlete)
    return athlete


async def list_athletes(session: AsyncSession, *, limit: int, offset: int) -> list[Athlete]:
    result = await session.execute(select(Athlete).order_by(Athlete.created_at.desc()).limit(limit).offset(offset))
    return list(result.scalars().all())


async def get_athlete(session: AsyncSession, athlete_id: uuid.UUID) -> Athlete | None:
    return await session.get(Athlete, athlete_id)
