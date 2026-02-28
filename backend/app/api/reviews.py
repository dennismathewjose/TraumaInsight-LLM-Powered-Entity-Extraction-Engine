"""Dashboard stats API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.review import OverviewStats
from app.services import extraction_service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=OverviewStats)
async def get_overview_stats(
    db: AsyncSession = Depends(get_db),
) -> OverviewStats:
    """Get dashboard overview statistics."""
    return await extraction_service.get_overview_stats(db)
