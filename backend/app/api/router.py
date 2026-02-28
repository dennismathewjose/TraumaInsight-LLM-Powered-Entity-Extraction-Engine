"""Main router aggregating all API sub-routers."""

from fastapi import APIRouter

from app.api.encounters import router as encounters_router
from app.api.extractions import router as extractions_router
from app.api.notes import router as notes_router
from app.api.patients import router as patients_router
from app.api.pipeline import router as pipeline_router
from app.api.reviews import router as reviews_router

api_router = APIRouter(prefix="/api")

api_router.include_router(patients_router)
api_router.include_router(encounters_router)
api_router.include_router(notes_router)
api_router.include_router(extractions_router)
api_router.include_router(reviews_router)
api_router.include_router(pipeline_router)
