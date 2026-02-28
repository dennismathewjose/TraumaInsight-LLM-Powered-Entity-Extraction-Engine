"""Pydantic schemas for Encounter responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EncounterRead(BaseModel):
    """Encounter response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    encounter_type: str
    start_date: datetime
    end_date: datetime | None = None
    primary_diagnosis_code: str | None = None
    primary_diagnosis_desc: str | None = None
