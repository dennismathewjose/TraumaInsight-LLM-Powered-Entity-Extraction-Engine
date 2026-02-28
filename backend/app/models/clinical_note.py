"""ClinicalNote ORM model."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class ClinicalNote(Base):
    """Represents a clinical note (op report, discharge summary, etc.)."""

    __tablename__ = "clinical_notes"

    id: str = Column(String, primary_key=True, default=lambda: str(uuid4()))
    patient_id: str = Column(String, ForeignKey("patients.id"), nullable=False)
    note_type: str = Column(String, nullable=False)  # operative_report / discharge_summary / radiology_report / progress_note
    content: str = Column(Text, nullable=False)
    author_role: str | None = Column(String, nullable=True)  # surgeon / radiologist / attending
    note_date: datetime = Column(DateTime, nullable=False)
    created_at: datetime = Column(DateTime, server_default=func.now())

    patient = relationship("Patient", back_populates="clinical_notes")
    extractions = relationship("Extraction", back_populates="source_note", lazy="selectin")
