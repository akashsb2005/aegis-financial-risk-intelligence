"""Versioned API route definitions."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.company import CompanyResponse
from app.schemas.financial_record import FinancialRecordResponse
from app.schemas.risk_assessment import (
    RiskAssessmentCreate,
    RiskAssessmentResponse,
    RiskSummaryResponse,
)
from app.services.company import CompanyNotFoundError, CompanyService
from app.services.financial_record import FinancialRecordService
from app.services.risk_assessment import RiskAssessmentService

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


@router.get("/companies", response_model=list[CompanyResponse], tags=["companies"])
def list_companies(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List companies in ascending ID order with pagination."""
    return CompanyService(db).list_companies(limit=limit, offset=offset)


@router.get(
    "/companies/{company_id}",
    response_model=CompanyResponse,
    responses={404: {"description": "Company not found"}},
    tags=["companies"],
)
def get_company(
    company_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
) -> CompanyResponse | JSONResponse:
    """Return one company by ID."""
    try:
        company = CompanyService(db).get_company(company_id)
    except CompanyNotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "COMPANY_NOT_FOUND",
                    "message": f"Company with ID {company_id} was not found.",
                }
            },
        )
    return CompanyResponse.model_validate(company)


@router.get(
    "/companies/{company_id}/financial-records",
    response_model=list[FinancialRecordResponse],
    responses={404: {"description": "Company not found"}},
    tags=["financial-records"],
)
def list_company_financial_records(
    company_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
) -> list[dict[str, Any]] | JSONResponse:
    """List financial records for an existing company."""
    try:
        return FinancialRecordService(db).list_for_company(company_id)
    except CompanyNotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "COMPANY_NOT_FOUND",
                    "message": f"Company with ID {company_id} was not found.",
                }
            },
        )


@router.get(
    "/companies/{company_id}/risk-assessments",
    response_model=list[RiskAssessmentResponse],
    responses={404: {"description": "Company not found"}},
    tags=["risk-assessments"],
)
def list_company_risk_assessments(
    company_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
) -> list[dict[str, Any]] | JSONResponse:
    """List assessment history for an existing company."""
    try:
        return RiskAssessmentService(db).list_for_company(company_id)
    except CompanyNotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "COMPANY_NOT_FOUND",
                    "message": f"Company with ID {company_id} was not found.",
                }
            },
        )


@router.post(
    "/companies/{company_id}/risk-assessments",
    response_model=RiskAssessmentResponse,
    status_code=201,
    responses={404: {"description": "Company not found"}},
    tags=["risk-assessments"],
)
def create_company_risk_assessment(
    company_id: Annotated[int, Path(gt=0)],
    assessment: RiskAssessmentCreate,
    db: Session = Depends(get_db),
) -> dict[str, Any] | JSONResponse:
    """Create an assessment through the existing PostgreSQL procedure."""
    try:
        return RiskAssessmentService(db).create_for_company(company_id, assessment)
    except CompanyNotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "COMPANY_NOT_FOUND",
                    "message": f"Company with ID {company_id} was not found.",
                }
            },
        )


@router.get(
    "/companies/{company_id}/risk-summary",
    response_model=RiskSummaryResponse,
    responses={404: {"description": "Company not found"}},
    tags=["risk-assessments"],
)
def get_company_risk_summary(
    company_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
) -> RiskSummaryResponse | JSONResponse:
    """Return current risk details from the existing database view."""
    try:
        summary = RiskAssessmentService(db).get_summary(company_id)
    except CompanyNotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "COMPANY_NOT_FOUND",
                    "message": f"Company with ID {company_id} was not found.",
                }
            },
        )
    return RiskSummaryResponse.model_validate(summary)
