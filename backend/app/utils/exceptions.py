"""Custom exception classes and FastAPI exception handlers."""

from fastapi import Request
from fastapi.responses import JSONResponse


class NotFoundException(Exception):
    """Raised when a requested resource is not found."""

    def __init__(self, detail: str = "Resource not found") -> None:
        self.detail = detail


class ConflictException(Exception):
    """Raised when an action conflicts with current state."""

    def __init__(self, detail: str = "Conflict") -> None:
        self.detail = detail


class ValidationException(Exception):
    """Raised for business-logic validation errors."""

    def __init__(self, detail: str = "Validation error") -> None:
        self.detail = detail


async def not_found_handler(_request: Request, exc: NotFoundException) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail, "status_code": 404})


async def conflict_handler(_request: Request, exc: ConflictException) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.detail, "status_code": 409})


async def validation_handler(_request: Request, exc: ValidationException) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.detail, "status_code": 422})


async def internal_error_handler(_request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500},
    )
