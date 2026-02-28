"""Pydantic schemas for review decisions, corrections, and dashboard stats."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReviewDecisionRead(BaseModel):
    """Review decision response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    extraction_id: str
    reviewer_id: str
    decision: str
    corrected_value: str | None = None
    notes: str | None = None
    decided_at: datetime | None = None


class CorrectRequest(BaseModel):
    """Request body for correcting an extraction value."""

    corrected_value: str
    notes: str | None = None


class OverviewStats(BaseModel):
    """Dashboard overview statistics."""

    total_patients: int
    pending_review: int
    completed: int
    total_extractions: int
    auto_filled: int
    needs_review: int
    reviewed: int
    auto_fill_rate: float
    avg_confidence: float
    estimated_time_saved_minutes: int
