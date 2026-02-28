"""Tests for extraction API endpoints (confirm / correct)."""

import pytest
from httpx import AsyncClient

from app.models.extraction import Extraction


@pytest.mark.asyncio
async def test_get_patient_extractions(async_client: AsyncClient, seed_extraction: Extraction):
    """GET /api/patients/{id}/extractions returns extractions."""
    resp = await async_client.get(f"/api/patients/{seed_extraction.patient_id}/extractions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["field_key"] == "primary_injury"
    assert data[0]["confidence_score"] == 0.95


@pytest.mark.asyncio
async def test_confirm_extraction(async_client: AsyncClient, seed_extraction: Extraction):
    """POST /api/extractions/{id}/confirm sets status to confirmed."""
    resp = await async_client.post(f"/api/extractions/{seed_extraction.id}/confirm")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "confirmed"


@pytest.mark.asyncio
async def test_confirm_already_reviewed(async_client: AsyncClient, seed_extraction: Extraction):
    """POST /api/extractions/{id}/confirm on already confirmed returns 409."""
    # First confirm
    await async_client.post(f"/api/extractions/{seed_extraction.id}/confirm")
    # Try again
    resp = await async_client.post(f"/api/extractions/{seed_extraction.id}/confirm")
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_correct_extraction(async_client: AsyncClient, seed_review_extraction: Extraction):
    """POST /api/extractions/{id}/correct updates extraction value."""
    resp = await async_client.post(
        f"/api/extractions/{seed_review_extraction.id}/correct",
        json={"corrected_value": "No — SSI only", "notes": "Confirmed on re-review"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "corrected"


@pytest.mark.asyncio
async def test_confirm_not_found(async_client: AsyncClient):
    """POST /api/extractions/{id}/confirm returns 404 for missing extraction."""
    resp = await async_client.post("/api/extractions/fake-id-000/confirm")
    assert resp.status_code == 404
