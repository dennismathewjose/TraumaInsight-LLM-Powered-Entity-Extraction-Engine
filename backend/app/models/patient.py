"""Patient ORM model."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class Patient(Base):
    """Represents a trauma patient in the registry."""

    __tablename__ = "patients"

    id: str = Column(String, primary_key=True)  # e.g. "P-10842"
    synthea_id: str | None = Column(String, nullable=True)
    first_name: str | None = Column(String, nullable=True)
    last_name: str | None = Column(String, nullable=True)
    age: int = Column(Integer, nullable=False)
    sex: str = Column(String(1), nullable=False)  # M/F
    admit_date: date = Column(Date, nullable=False)
    discharge_date: date | None = Column(Date, nullable=True)
    mechanism_of_injury: str = Column(String, nullable=False)
    iss: int | None = Column(Integer, nullable=True)  # Injury Severity Score
    los: int | None = Column(Integer, nullable=True)  # Length of Stay (days)
    status: str = Column(String, default="pending")  # pending/review/completed
    priority: str = Column(String, default="medium")  # low/medium/high
    created_at: datetime = Column(DateTime, server_default=func.now())
    updated_at: datetime | None = Column(DateTime, onupdate=func.now())

    # Relationships
    encounters = relationship("Encounter", back_populates="patient", lazy="selectin")
    clinical_notes = relationship("ClinicalNote", back_populates="patient", lazy="selectin")
    extractions = relationship("Extraction", back_populates="patient", lazy="selectin")
