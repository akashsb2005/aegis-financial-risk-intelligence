"""Versioned API route definitions."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
def versioned_health_check() -> dict[str, str]:
    """Report that the versioned API is responsive."""
    return {"status": "ok"}
