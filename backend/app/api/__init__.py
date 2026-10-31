"""Versioned API route definitions."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter()


@router.get("/health", tags=["health"])
def versioned_health_check() -> dict[str, str]:
    """Report that the versioned API is responsive."""
    return {"status": "ok"}


@router.get("/health/db", tags=["health"])
def database_health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Check database connectivity with a minimal query."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}
