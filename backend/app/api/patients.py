"""Patient API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.clinical_note import ClinicalNoteRead
from app.schemas.extraction import ExtractionRead, PatientFormResponse
from app.schemas.patient import PatientListItem, PatientRead, PatientStatusUpdate
from app.services import extraction_service, patient_service

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=list[PatientListItem])
async def list_patients(
    status: str | None = Query(None, description="Filter by status: pending/review/completed"),
    priority: str | None = Query(None, description="Filter by priority: low/medium/high"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[PatientListItem]:
    """List all patients with summary extraction stats."""
    return await patient_service.list_patients(db, status=status, priority=priority, limit=limit, offset=offset)


@router.get("/{patient_id}", response_model=PatientRead)
async def get_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
) -> PatientRead:
    """Get a single patient by ID."""
    return await patient_service.get_patient(db, patient_id)


@router.get("/{patient_id}/form", response_model=PatientFormResponse)
async def get_patient_form(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
) -> PatientFormResponse:
    """Get the complete registry form data for a patient, grouped by section."""
    return await patient_service.get_patient_form(db, patient_id)


@router.patch("/{patient_id}/status", response_model=PatientRead)
async def update_patient_status(
    patient_id: str,
    body: PatientStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> PatientRead:
    """Update a patient's status (pending/review/completed)."""
    return await patient_service.update_patient_status(db, patient_id, body.status)


@router.get("/{patient_id}/notes", response_model=list[ClinicalNoteRead])
async def get_patient_notes(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[ClinicalNoteRead]:
    """Get all clinical notes for a patient."""
    from sqlalchemy import select
    from app.models.clinical_note import ClinicalNote
    from app.models.patient import Patient
    from app.utils.exceptions import NotFoundException

    # Verify patient exists
    patient_result = await db.execute(select(Patient).where(Patient.id == patient_id))
    if not patient_result.scalar_one_or_none():
        raise NotFoundException(f"Patient {patient_id} not found")

    result = await db.execute(
        select(ClinicalNote)
        .where(ClinicalNote.patient_id == patient_id)
        .order_by(ClinicalNote.note_date)
    )
    notes = result.scalars().all()
    return [ClinicalNoteRead.model_validate(n) for n in notes]


@router.get("/{patient_id}/extractions", response_model=list[ExtractionRead])
async def get_patient_extractions(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[ExtractionRead]:
    """Get all extractions for a patient."""
    return await extraction_service.get_patient_extractions(db, patient_id)
