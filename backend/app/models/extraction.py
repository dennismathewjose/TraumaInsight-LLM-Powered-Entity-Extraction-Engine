"""Extraction ORM model."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class Extraction(Base):
    """Represents a single extracted registry field value."""

    __tablename__ = "extractions"

    id: str = Column(String, primary_key=True, default=lambda: str(uuid4()))
    patient_id: str = Column(String, ForeignKey("patients.id"), nullable=False)
    source_note_id: str | None = Column(String, ForeignKey("clinical_notes.id"), nullable=True)

    # Registry form field info
    section: str = Column(String, nullable=False)  # injuries/procedures/complications/severity/discharge
    field_label: str = Column(String, nullable=False)  # e.g. "Primary Injury"
    field_key: str = Column(String, nullable=False)  # e.g. "primary_injury"

    # Extraction result
    extracted_value: str = Column(String, nullable=False)
    confidence_score: float = Column(Float, nullable=False)  # 0.0–1.0
    status: str = Column(String, default="auto")  # auto/review/confirmed/corrected

    # Evidence
    citation_text: str | None = Column(Text, nullable=True)
    source_note_type: str | None = Column(String, nullable=True)
    conflict_reason: str | None = Column(Text, nullable=True)

    # Extraction metadata
    extraction_method: str = Column(String, default="rag")  # rag/keyword/direct_llm
    extracted_at: datetime = Column(DateTime, server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="extractions")
    source_note = relationship("ClinicalNote", back_populates="extractions")
    review_decision = relationship(
        "ReviewDecision", back_populates="extraction", uselist=False, lazy="selectin"
    )
