"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api import router as api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    application = FastAPI(title=settings.app_name, version=settings.app_version)

    @application.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        """Report that the API process is responsive."""
        return {"status": "ok"}

    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
