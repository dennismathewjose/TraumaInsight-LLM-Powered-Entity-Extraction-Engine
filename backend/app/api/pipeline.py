"""Pipeline API endpoints — run extraction for patients."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, Query

# Ensure backend/ is on sys.path for pipeline imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run/{patient_id}")
async def run_pipeline(patient_id: str, model: str = Query("llama3")) -> dict:
    """Run the full extraction pipeline for a single patient.

    This is a synchronous operation — the client waits while the pipeline runs
    (typically 30-60 seconds per patient).
    """
    from pipeline.orchestrator import process_patient

    result = process_patient(patient_id, model=model)
    return result


@router.post("/run-all")
async def run_pipeline_all(
    limit: int | None = Query(None),
    model: str = Query("llama3"),
) -> dict:
    """Run the extraction pipeline for all patients.

    Accepts optional `limit` and `model` query parameters.
    """
    from pipeline.orchestrator import process_all_patients

    result = process_all_patients(model=model, limit=limit)
    return result
