"""Business logic for review decisions (confirm / correct)."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.extraction import Extraction
from app.models.review_decision import ReviewDecision
from app.schemas.extraction import ExtractionRead
from app.utils.exceptions import ConflictException, NotFoundException


async def confirm_extraction(db: AsyncSession, extraction_id: str) -> ExtractionRead:
    """Confirm an AI-extracted value as correct."""
    result = await db.execute(
        select(Extraction).where(Extraction.id == extraction_id)
    )
    extraction = result.scalar_one_or_none()
    if not extraction:
        raise NotFoundException(f"Extraction {extraction_id} not found")

    if extraction.status in ("confirmed", "corrected"):
        raise ConflictException(
            f"Extraction {extraction_id} has already been reviewed "
            f"(status: {extraction.status})"
        )

    extraction.status = "confirmed"

    review = ReviewDecision(
        id=str(uuid4()),
        extraction_id=extraction_id,
        reviewer_id="registrar_1",
        decision="confirm",
    )
    db.add(review)
    await db.flush()

    # Re-fetch with relationships loaded
    refreshed = await db.execute(
        select(Extraction).where(Extraction.id == extraction_id)
    )
    updated = refreshed.scalar_one()
    return ExtractionRead.model_validate(updated)


async def correct_extraction(
    db: AsyncSession,
    extraction_id: str,
    corrected_value: str,
    notes: str | None = None,
) -> ExtractionRead:
    """Correct an AI-extracted value with the registrar's value."""
    result = await db.execute(
        select(Extraction).where(Extraction.id == extraction_id)
    )
    extraction = result.scalar_one_or_none()
    if not extraction:
        raise NotFoundException(f"Extraction {extraction_id} not found")

    if extraction.status in ("confirmed", "corrected"):
        raise ConflictException(
            f"Extraction {extraction_id} has already been reviewed "
            f"(status: {extraction.status})"
        )

    extraction.status = "corrected"

    review = ReviewDecision(
        id=str(uuid4()),
        extraction_id=extraction_id,
        reviewer_id="registrar_1",
        decision="correct",
        corrected_value=corrected_value,
        notes=notes,
    )
    db.add(review)
    await db.flush()

    # Re-fetch with relationships loaded
    refreshed = await db.execute(
        select(Extraction).where(Extraction.id == extraction_id)
    )
    updated = refreshed.scalar_one()
    return ExtractionRead.model_validate(updated)
