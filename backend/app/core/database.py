"""SQLAlchemy engine, session factory, and FastAPI session dependency."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def _create_engine() -> Engine:
    """Create the database engine from application settings."""
    database_url = get_settings().database_url
    if not database_url:
        raise RuntimeError(
            "AEGIS_DATABASE_URL is not configured. Set it in backend/.env or the "
            "repository root .env file."
        )
    return create_engine(database_url, pool_pre_ping=True)


engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and always close it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
