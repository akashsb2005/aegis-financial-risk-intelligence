"""Application logic for company risk assessments and audit history."""

from typing import Any

from sqlalchemy.orm import Session

from app.repositories.risk_assessment import RiskAssessmentRepository
from app.schemas.risk_assessment import RiskAssessmentCreate
from app.services.company import CompanyService


class RiskAssessmentService:
    """Provide company-scoped assessment history, audit history, and summaries."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._companies = CompanyService(session)
        self._repository = RiskAssessmentRepository(session)

    def list_for_company(self, company_id: int) -> list[dict[str, Any]]:
        self._companies.get_company(company_id)
        return self._repository.list_for_company(company_id)

    def list_audit_for_company(
        self, company_id: int, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Return audit snapshots only after verifying the company exists."""
        self._companies.get_company(company_id)
        return self._repository.list_audit_for_company(company_id, limit, offset)

    def create_for_company(
        self,
        company_id: int,
        assessment: RiskAssessmentCreate,
    ) -> dict[str, Any]:
        self._companies.get_company(company_id)
        created = self._repository.create_for_company(company_id, assessment)
        self._session.commit()
        return created

    def get_summary(self, company_id: int) -> dict[str, Any]:
        company = self._companies.get_company(company_id)
        return self._repository.get_summary(company_id, str(company["company_name"]))
