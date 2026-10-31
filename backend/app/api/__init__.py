"""Versioned API route definitions."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.auth import require_authenticated_user, require_role
from app.core.database import get_db
from app.schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    LoginResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.schemas.company import CompanyResponse
from app.schemas.financial_record import FinancialRecordResponse
from app.schemas.risk_assessment import (
    RiskAssessmentCreate,
    RiskAssessmentResponse,
    RiskSummaryResponse,
)
from app.services.auth import AuthService
from app.services.company import CompanyNotFoundError, CompanyService
from app.services.financial_record import FinancialRecordService
from app.services.risk_assessment import RiskAssessmentService

router = APIRouter()


@router.post("/auth/register", response_model=RegisterResponse, status_code=201, tags=["auth"])
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Register a new ANALYST account."""
    return {"user": AuthService(db).register(request)}


@router.post("/auth/login", response_model=LoginResponse, tags=["auth"])
def login(request: LoginRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Authenticate credentials and create a server-managed session."""
    return AuthService(db).login(request)


@router.post("/auth/logout", tags=["auth"])
def logout(
    user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Revoke the current authenticated session."""
    AuthService(db).logout(user)
    return {"message": "Logged out successfully."}


@router.post(
    "/auth/password-reset/request",
    response_model=PasswordResetRequestResponse,
    response_model_exclude_none=True,
    tags=["auth"],
)
def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Create a reset token without revealing whether the email exists."""
    return AuthService(db).request_password_reset(request)


@router.post("/auth/password-reset/confirm", tags=["auth"])
def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Consume a valid reset token and change the account password."""
    AuthService(db).confirm_password_reset(request)
    return {"message": "Password reset completed."}


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
    _user: AuthenticatedUser = Depends(require_authenticated_user),
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
    _user: AuthenticatedUser = Depends(require_authenticated_user),
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
    _user: AuthenticatedUser = Depends(require_authenticated_user),
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
    _user: AuthenticatedUser = Depends(require_authenticated_user),
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
    user: AuthenticatedUser = Depends(require_role("ANALYST")),
    db: Session = Depends(get_db),
) -> dict[str, Any] | JSONResponse:
    """Create an assessment through the existing PostgreSQL procedure."""
    try:
        assessment = assessment.model_copy(update={"assessed_by": user.user_id})
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
    _user: AuthenticatedUser = Depends(require_authenticated_user),
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
