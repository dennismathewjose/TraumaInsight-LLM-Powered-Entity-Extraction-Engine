"""Business logic for extraction and dashboard stats."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.extraction import Extraction
from app.models.patient import Patient
from app.schemas.extraction import ExtractionRead
from app.schemas.review import OverviewStats


async def get_patient_extractions(
    db: AsyncSession, patient_id: str
) -> list[ExtractionRead]:
    """Get all extractions for a patient."""
    # Verify patient exists
    patient_result = await db.execute(select(Patient).where(Patient.id == patient_id))
    if not patient_result.scalar_one_or_none():
        from app.utils.exceptions import NotFoundException

        raise NotFoundException(f"Patient {patient_id} not found")

    result = await db.execute(
        select(Extraction)
        .options(selectinload(Extraction.review_decision))
        .where(Extraction.patient_id == patient_id)
        .order_by(Extraction.section, Extraction.field_key)
    )
    extractions = result.scalars().all()
    return [ExtractionRead.model_validate(e) for e in extractions]


async def get_overview_stats(db: AsyncSession) -> OverviewStats:
    """Compute dashboard aggregate statistics."""
    # Patient counts
    total_patients_result = await db.execute(select(func.count(Patient.id)))
    total_patients = total_patients_result.scalar() or 0

    pending_result = await db.execute(
        select(func.count(Patient.id)).where(Patient.status == "pending")
    )
    pending = pending_result.scalar() or 0

    review_patients_result = await db.execute(
        select(func.count(Patient.id)).where(Patient.status == "review")
    )
    review_patients = review_patients_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count(Patient.id)).where(Patient.status == "completed")
    )
    completed = completed_result.scalar() or 0

    # Extraction counts
    total_ext_result = await db.execute(select(func.count(Extraction.id)))
    total_extractions = total_ext_result.scalar() or 0

    auto_result = await db.execute(
        select(func.count(Extraction.id)).where(Extraction.status == "auto")
    )
    auto_filled = auto_result.scalar() or 0

    review_result = await db.execute(
        select(func.count(Extraction.id)).where(Extraction.status == "review")
    )
    needs_review = review_result.scalar() or 0

    confirmed_result = await db.execute(
        select(func.count(Extraction.id)).where(Extraction.status == "confirmed")
    )
    confirmed = confirmed_result.scalar() or 0

    corrected_result = await db.execute(
        select(func.count(Extraction.id)).where(Extraction.status == "corrected")
    )
    corrected = corrected_result.scalar() or 0

    reviewed = confirmed + corrected

    # Average confidence
    avg_conf_result = await db.execute(select(func.avg(Extraction.confidence_score)))
    avg_confidence = avg_conf_result.scalar() or 0.0

    # Auto-fill rate
    auto_fill_rate = (auto_filled / total_extractions * 100) if total_extractions > 0 else 0.0

    # Estimated time saved: ~15 min per patient with extractions
    patients_with_ext_result = await db.execute(
        select(func.count(func.distinct(Extraction.patient_id)))
    )
    patients_with_extractions = patients_with_ext_result.scalar() or 0
    estimated_time_saved = patients_with_extractions * 15

    return OverviewStats(
        total_patients=total_patients,
        pending_review=pending + review_patients,
        completed=completed,
        total_extractions=total_extractions,
        auto_filled=auto_filled,
        needs_review=needs_review,
        reviewed=reviewed,
        auto_fill_rate=round(auto_fill_rate, 1),
        avg_confidence=round(avg_confidence * 100, 1),
        estimated_time_saved_minutes=estimated_time_saved,
    )
