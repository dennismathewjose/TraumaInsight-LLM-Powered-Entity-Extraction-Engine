"""Pytest fixtures and test database setup."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import date, datetime
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database import Base, get_db
from app.main import app
from app.models.clinical_note import ClinicalNote
from app.models.extraction import Extraction
from app.models.patient import Patient

# ── Test database (async SQLite) ─────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Override the default event loop to be session-scoped."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = _override_get_db


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP client bound to the test app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a raw DB session for seeding test data."""
    async with test_session_factory() as session:
        yield session
        await session.commit()


@pytest_asyncio.fixture
async def seed_patient(db_session: AsyncSession) -> Patient:
    """Create a single test patient."""
    patient = Patient(
        id="P-99001",
        synthea_id="test-uuid-001",
        first_name="Test",
        last_name="Patient",
        age=45,
        sex="M",
        admit_date=date(2025, 1, 15),
        discharge_date=date(2025, 1, 20),
        mechanism_of_injury="Motor vehicle collision",
        iss=16,
        los=5,
        status="pending",
        priority="high",
    )
    db_session.add(patient)
    await db_session.flush()
    return patient


@pytest_asyncio.fixture
async def seed_note(db_session: AsyncSession, seed_patient: Patient) -> ClinicalNote:
    """Create a test clinical note."""
    note = ClinicalNote(
        id=str(uuid4()),
        patient_id=seed_patient.id,
        note_type="operative_report",
        content="The patient had a splenic laceration. Splenectomy was performed.",
        author_role="surgeon",
        note_date=datetime(2025, 1, 15, 10, 0),
    )
    db_session.add(note)
    await db_session.flush()
    return note


@pytest_asyncio.fixture
async def seed_extraction(
    db_session: AsyncSession, seed_patient: Patient, seed_note: ClinicalNote
) -> Extraction:
    """Create a test extraction."""
    extraction = Extraction(
        id=str(uuid4()),
        patient_id=seed_patient.id,
        source_note_id=seed_note.id,
        section="injuries",
        field_label="Primary Injury",
        field_key="primary_injury",
        extracted_value="Splenic laceration",
        confidence_score=0.95,
        status="auto",
        citation_text="The patient had a splenic laceration.",
        source_note_type="operative_report",
        extraction_method="rag",
    )
    db_session.add(extraction)
    await db_session.flush()
    return extraction


@pytest_asyncio.fixture
async def seed_review_extraction(
    db_session: AsyncSession, seed_patient: Patient, seed_note: ClinicalNote
) -> Extraction:
    """Create an extraction that needs review."""
    extraction = Extraction(
        id=str(uuid4()),
        patient_id=seed_patient.id,
        source_note_id=seed_note.id,
        section="complications",
        field_label="Complications Present",
        field_key="complications_present",
        extracted_value="Yes — SSI suspected",
        confidence_score=0.65,
        status="review",
        citation_text="Postoperative course was c/b mild wound erythema.",
        source_note_type="discharge_summary",
        conflict_reason="Operative report and discharge summary disagree.",
        extraction_method="rag",
    )
    db_session.add(extraction)
    await db_session.flush()
    return extraction
