"""Tests for patient API endpoints."""

import pytest
from httpx import AsyncClient

from app.models.patient import Patient


@pytest.mark.asyncio
async def test_list_patients_empty(async_client: AsyncClient):
    """GET /api/patients returns empty list when no patients exist."""
    resp = await async_client.get("/api/patients")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_patients(async_client: AsyncClient, seed_patient: Patient):
    """GET /api/patients returns seeded patients."""
    resp = await async_client.get("/api/patients")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["id"] == seed_patient.id
    assert data[0]["mechanism_of_injury"] == "Motor vehicle collision"


@pytest.mark.asyncio
async def test_list_patients_filter_status(async_client: AsyncClient, seed_patient: Patient):
    """GET /api/patients?status=pending filters correctly."""
    resp = await async_client.get("/api/patients", params={"status": "pending"})
    assert resp.status_code == 200
    data = resp.json()
    assert all(p["status"] == "pending" for p in data)


@pytest.mark.asyncio
async def test_get_patient(async_client: AsyncClient, seed_patient: Patient):
    """GET /api/patients/{id} returns the correct patient."""
    resp = await async_client.get(f"/api/patients/{seed_patient.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == seed_patient.id
    assert data["age"] == 45
    assert data["sex"] == "M"


@pytest.mark.asyncio
async def test_get_patient_not_found(async_client: AsyncClient):
    """GET /api/patients/{id} returns 404 for missing patient."""
    resp = await async_client.get("/api/patients/P-99999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_patient_form(async_client: AsyncClient, seed_extraction):
    """GET /api/patients/{id}/form returns grouped sections."""
    resp = await async_client.get(f"/api/patients/{seed_extraction.patient_id}/form")
    assert resp.status_code == 200
    data = resp.json()
    assert "patient" in data
    assert "sections" in data
    assert "summary" in data
    assert data["summary"]["total_fields"] >= 1


@pytest.mark.asyncio
async def test_update_patient_status(async_client: AsyncClient, seed_patient: Patient):
    """PATCH /api/patients/{id}/status updates status."""
    resp = await async_client.patch(
        f"/api/patients/{seed_patient.id}/status",
        json={"status": "completed"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_update_patient_status_invalid(async_client: AsyncClient, seed_patient: Patient):
    """PATCH /api/patients/{id}/status rejects invalid status."""
    resp = await async_client.patch(
        f"/api/patients/{seed_patient.id}/status",
        json={"status": "invalid_status"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_patient_notes(async_client: AsyncClient, seed_note):
    """GET /api/patients/{id}/notes returns notes."""
    resp = await async_client.get(f"/api/patients/{seed_note.patient_id}/notes")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["note_type"] == "operative_report"
