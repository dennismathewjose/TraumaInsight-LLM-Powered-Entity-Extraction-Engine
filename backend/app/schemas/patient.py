"""Pydantic schemas for Patient-related requests and responses."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PatientBase(BaseModel):
    """Shared patient fields."""

    id: str
    first_name: str | None = None
    last_name: str | None = None
    age: int
    sex: str
    admit_date: date
    discharge_date: date | None = None
    mechanism_of_injury: str
    iss: int | None = None
    los: int | None = None
    status: str = "pending"
    priority: str = "medium"


class PatientRead(PatientBase):
    """Full patient detail response."""

    model_config = ConfigDict(from_attributes=True)

    synthea_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PatientListItem(PatientBase):
    """Patient in a list view, with extraction summary stats."""

    model_config = ConfigDict(from_attributes=True)

    total_extractions: int = 0
    auto_filled: int = 0
    needs_review: int = 0


class PatientStatusUpdate(BaseModel):
    """Request body for updating patient status."""

    status: str  # pending / review / completed
