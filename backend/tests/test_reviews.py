"""Tests for stats and health check endpoints."""

import pytest
from httpx import AsyncClient

from app.models.extraction import Extraction
from app.models.patient import Patient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """GET /health returns healthy status."""
    resp = await async_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_overview_stats_empty(async_client: AsyncClient):
    """GET /api/stats/overview returns zeroed stats when empty."""
    resp = await async_client.get("/api/stats/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_patients"] == 0
    assert data["total_extractions"] == 0
    assert data["auto_fill_rate"] == 0.0


@pytest.mark.asyncio
async def test_overview_stats_with_data(
    async_client: AsyncClient,
    seed_patient: Patient,
    seed_extraction: Extraction,
    seed_review_extraction: Extraction,
):
    """GET /api/stats/overview returns correct counts."""
    resp = await async_client.get("/api/stats/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_patients"] == 1
    assert data["total_extractions"] == 2
    assert data["auto_filled"] == 1
    assert data["needs_review"] == 1
    assert data["pending_review"] == 1  # patient is pending


@pytest.mark.asyncio
async def test_pipeline_placeholder(async_client: AsyncClient):
    """POST /api/pipeline/run/{id} returns 501."""
    resp = await async_client.post("/api/pipeline/run/P-99001")
    assert resp.status_code == 501
    assert "Phase 2" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_pipeline_run_all_placeholder(async_client: AsyncClient):
    """POST /api/pipeline/run-all returns 501."""
    resp = await async_client.post("/api/pipeline/run-all")
    assert resp.status_code == 501
