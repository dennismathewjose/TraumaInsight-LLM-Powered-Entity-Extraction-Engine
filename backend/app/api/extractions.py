"""Extraction review API endpoints (confirm / correct)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.extraction import ExtractionRead
from app.schemas.review import CorrectRequest
from app.services import review_service

router = APIRouter(prefix="/extractions", tags=["extractions"])


@router.post("/{extraction_id}/confirm", response_model=ExtractionRead)
async def confirm_extraction(
    extraction_id: str,
    db: AsyncSession = Depends(get_db),
) -> ExtractionRead:
    """Registrar confirms the AI-extracted value is correct."""
    return await review_service.confirm_extraction(db, extraction_id)


@router.post("/{extraction_id}/correct", response_model=ExtractionRead)
async def correct_extraction(
    extraction_id: str,
    body: CorrectRequest,
    db: AsyncSession = Depends(get_db),
) -> ExtractionRead:
    """Registrar corrects the AI-extracted value."""
    return await review_service.correct_extraction(
        db, extraction_id, body.corrected_value, body.notes
    )
