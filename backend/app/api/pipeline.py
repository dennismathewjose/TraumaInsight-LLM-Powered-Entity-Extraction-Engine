"""Pipeline placeholder endpoints (Phase 2)."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run/{patient_id}")
async def run_pipeline(patient_id: str) -> JSONResponse:
    """Placeholder: Run extraction pipeline for a single patient."""
    return JSONResponse(
        status_code=501,
        content={
            "detail": "Extraction pipeline will be available in Phase 2",
            "patient_id": patient_id,
        },
    )


@router.post("/run-all")
async def run_pipeline_all() -> JSONResponse:
    """Placeholder: Run extraction pipeline for all patients."""
    return JSONResponse(
        status_code=501,
        content={"detail": "Extraction pipeline will be available in Phase 2"},
    )
