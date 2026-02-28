"""Encounter API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.encounter import Encounter
from app.schemas.encounter import EncounterRead

router = APIRouter(prefix="/encounters", tags=["encounters"])


@router.get("/{encounter_id}", response_model=EncounterRead)
async def get_encounter(
    encounter_id: str,
    db: AsyncSession = Depends(get_db),
) -> EncounterRead:
    """Get a single encounter by ID."""
    from app.utils.exceptions import NotFoundException

    result = await db.execute(select(Encounter).where(Encounter.id == encounter_id))
    encounter = result.scalar_one_or_none()
    if not encounter:
        raise NotFoundException(f"Encounter {encounter_id} not found")
    return EncounterRead.model_validate(encounter)
