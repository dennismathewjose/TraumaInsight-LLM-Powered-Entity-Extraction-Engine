"""Clinical notes API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.clinical_note import ClinicalNote
from app.schemas.clinical_note import ClinicalNoteRead
from app.utils.exceptions import NotFoundException

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/{note_id}", response_model=ClinicalNoteRead)
async def get_note(
    note_id: str,
    db: AsyncSession = Depends(get_db),
) -> ClinicalNoteRead:
    """Get a single clinical note by ID."""
    result = await db.execute(select(ClinicalNote).where(ClinicalNote.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise NotFoundException(f"Note {note_id} not found")
    return ClinicalNoteRead.model_validate(note)
