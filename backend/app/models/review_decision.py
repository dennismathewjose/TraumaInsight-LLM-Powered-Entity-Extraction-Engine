"""ReviewDecision ORM model."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class ReviewDecision(Base):
    """Represents a registrar's confirm/correct decision on an extraction."""

    __tablename__ = "review_decisions"

    id: str = Column(String, primary_key=True, default=lambda: str(uuid4()))
    extraction_id: str = Column(String, ForeignKey("extractions.id"), nullable=False)
    reviewer_id: str = Column(String, nullable=False)  # e.g. "registrar_1"
    decision: str = Column(String, nullable=False)  # confirm/correct
    corrected_value: str | None = Column(String, nullable=True)
    notes: str | None = Column(Text, nullable=True)
    decided_at: datetime = Column(DateTime, server_default=func.now())

    extraction = relationship("Extraction", back_populates="review_decision")
