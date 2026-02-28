"""Encounter ORM model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.database import Base


class Encounter(Base):
    """Represents a clinical encounter (emergency, inpatient, ICU)."""

    __tablename__ = "encounters"

    id: str = Column(String, primary_key=True)
    patient_id: str = Column(String, ForeignKey("patients.id"), nullable=False)
    encounter_type: str = Column(String, nullable=False)  # emergency/inpatient/icu
    start_date: datetime = Column(DateTime, nullable=False)
    end_date: datetime | None = Column(DateTime, nullable=True)
    primary_diagnosis_code: str | None = Column(String, nullable=True)  # ICD-10
    primary_diagnosis_desc: str | None = Column(String, nullable=True)

    patient = relationship("Patient", back_populates="encounters")
