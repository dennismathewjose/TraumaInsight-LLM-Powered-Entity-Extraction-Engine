"""Business logic for patient operations."""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.extraction import Extraction
from app.models.patient import Patient
from app.schemas.extraction import (
    ExtractionField,
    FormSection,
    FormSummary,
    PatientFormResponse,
)
from app.schemas.patient import PatientListItem, PatientRead
from app.schemas.review import ReviewDecisionRead
from app.utils.exceptions import NotFoundException


async def list_patients(
    db: AsyncSession,
    status: str | None = None,
    priority: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[PatientListItem]:
    """List patients with summary extraction stats."""
    query = select(Patient).options(selectinload(Patient.extractions))

    if status:
        query = query.where(Patient.status == status)
    if priority:
        query = query.where(Patient.priority == priority)

    query = query.offset(offset).limit(limit).order_by(Patient.created_at.desc())
    result = await db.execute(query)
    patients = result.scalars().all()

    items: list[PatientListItem] = []
    for p in patients:
        extractions = p.extractions or []
        total = len(extractions)
        auto = sum(1 for e in extractions if e.status == "auto")
        review = sum(1 for e in extractions if e.status == "review")
        items.append(
            PatientListItem(
                id=p.id,
                first_name=p.first_name,
                last_name=p.last_name,
                age=p.age,
                sex=p.sex,
                admit_date=p.admit_date,
                discharge_date=p.discharge_date,
                mechanism_of_injury=p.mechanism_of_injury,
                iss=p.iss,
                los=p.los,
                status=p.status,
                priority=p.priority,
                total_extractions=total,
                auto_filled=auto,
                needs_review=review,
            )
        )
    return items


async def get_patient(db: AsyncSession, patient_id: str) -> PatientRead:
    """Get a single patient by ID."""
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise NotFoundException(f"Patient {patient_id} not found")
    return PatientRead.model_validate(patient)


async def get_patient_form(db: AsyncSession, patient_id: str) -> PatientFormResponse:
    """Build the complete registry form response for a patient."""
    # Fetch patient
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise NotFoundException(f"Patient {patient_id} not found")

    # Fetch extractions with review decisions
    ext_result = await db.execute(
        select(Extraction)
        .options(selectinload(Extraction.review_decision))
        .where(Extraction.patient_id == patient_id)
        .order_by(Extraction.section, Extraction.field_key)
    )
    extractions = ext_result.scalars().all()

    # Group by section
    section_map: dict[str, list[ExtractionField]] = defaultdict(list)
    counts = {"auto": 0, "review": 0, "confirmed": 0, "corrected": 0}

    for ext in extractions:
        review = None
        if ext.review_decision:
            review = ReviewDecisionRead.model_validate(ext.review_decision)

        field = ExtractionField(
            id=ext.id,
            field_key=ext.field_key,
            field_label=ext.field_label,
            extracted_value=ext.extracted_value,
            confidence_score=ext.confidence_score,
            status=ext.status,
            citation_text=ext.citation_text,
            source_note_type=ext.source_note_type,
            conflict_reason=ext.conflict_reason,
            review_decision=review,
        )
        section_map[ext.section].append(field)

        if ext.status in counts:
            counts[ext.status] += 1

    # Build sections in a defined order
    section_order = ["injuries", "procedures", "complications", "severity", "discharge"]
    sections: list[FormSection] = []
    for section_key in section_order:
        if section_key in section_map:
            sections.append(
                FormSection(
                    title=section_key.upper(),
                    fields=section_map[section_key],
                )
            )
    # Add any remaining sections not in the predefined order
    for section_key, fields in section_map.items():
        if section_key not in section_order:
            sections.append(FormSection(title=section_key.upper(), fields=fields))

    total = len(extractions)
    summary = FormSummary(
        total_fields=total,
        auto_filled=counts["auto"],
        needs_review=counts["review"],
        confirmed=counts["confirmed"],
        corrected=counts["corrected"],
    )

    return PatientFormResponse(
        patient=PatientRead.model_validate(patient),
        sections=sections,
        summary=summary,
    )


async def update_patient_status(
    db: AsyncSession, patient_id: str, new_status: str
) -> PatientRead:
    """Update a patient's status."""
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise NotFoundException(f"Patient {patient_id} not found")

    valid_statuses = {"pending", "review", "completed"}
    if new_status not in valid_statuses:
        from app.utils.exceptions import ValidationException

        raise ValidationException(
            f"Invalid status '{new_status}'. Must be one of: {valid_statuses}"
        )

    patient.status = new_status
    await db.flush()
    await db.refresh(patient)
    return PatientRead.model_validate(patient)
