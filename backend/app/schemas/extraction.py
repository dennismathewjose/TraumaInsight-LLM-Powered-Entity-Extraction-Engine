"""Pydantic schemas for Extraction responses and form data."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.review import ReviewDecisionRead


class ExtractionRead(BaseModel):
    """Full extraction response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    source_note_id: str | None = None
    section: str
    field_label: str
    field_key: str
    extracted_value: str
    confidence_score: float
    status: str
    citation_text: str | None = None
    source_note_type: str | None = None
    conflict_reason: str | None = None
    extraction_method: str = "rag"
    extracted_at: datetime | None = None
    review_decision: ReviewDecisionRead | None = None


class ExtractionField(BaseModel):
    """A single field in the registry form view."""

    id: str
    field_key: str
    field_label: str
    extracted_value: str
    confidence_score: float
    status: str
    citation_text: str | None = None
    source_note_type: str | None = None
    conflict_reason: str | None = None
    review_decision: ReviewDecisionRead | None = None


class FormSection(BaseModel):
    """A section of the registry form (e.g. INJURIES, PROCEDURES)."""

    title: str
    fields: list[ExtractionField]


class FormSummary(BaseModel):
    """Summary counts for the form view."""

    total_fields: int
    auto_filled: int
    needs_review: int
    confirmed: int
    corrected: int


class PatientFormResponse(BaseModel):
    """Complete registry form response for a patient."""

    patient: "PatientRead"
    sections: list[FormSection]
    summary: FormSummary


# Avoid circular import — resolve forward ref at module level
from app.schemas.patient import PatientRead  # noqa: E402

PatientFormResponse.model_rebuild()
