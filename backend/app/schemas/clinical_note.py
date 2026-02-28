"""Pydantic schemas for ClinicalNote responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClinicalNoteRead(BaseModel):
    """Full clinical note response (includes content)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    note_type: str
    content: str
    author_role: str | None = None
    note_date: datetime
    created_at: datetime | None = None


class ClinicalNoteSummary(BaseModel):
    """Clinical note without full content (for list views)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    note_type: str
    author_role: str | None = None
    note_date: datetime
