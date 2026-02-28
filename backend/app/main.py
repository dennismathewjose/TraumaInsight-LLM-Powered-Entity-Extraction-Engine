"""FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.router import api_router
from app.config import get_settings
from app.database import engine, get_db
from app.utils.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
    conflict_handler,
    internal_error_handler,
    not_found_handler,
    validation_handler,
)

# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("traumainsight")


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown lifecycle."""
    logger.info("TraumaInsight API starting up …")
    yield
    logger.info("TraumaInsight API shutting down …")
    await engine.dispose()


# ── App ──────────────────────────────────────────────────────────────────────

settings = get_settings()

app = FastAPI(
    title="TraumaInsight API",
    description=(
        "Clinical AI backend for automated trauma registry chart abstraction. "
        "Extracts structured data from clinical notes and supports registrar review."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(NotFoundException, not_found_handler)  # type: ignore[arg-type]
app.add_exception_handler(ConflictException, conflict_handler)  # type: ignore[arg-type]
app.add_exception_handler(ValidationException, validation_handler)  # type: ignore[arg-type]

# Routes
app.include_router(api_router)


# ── Health check ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["health"])
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Check API and database connectivity."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as exc:
        logger.error("Health check failed: %s", exc)
        return {"status": "unhealthy", "error": str(exc)}
