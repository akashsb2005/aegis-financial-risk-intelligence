"""Application logic for company risk assessments."""

from typing import Any

from sqlalchemy.orm import Session

from app.repositories.risk_assessment import RiskAssessmentRepository
from app.schemas.risk_assessment import RiskAssessmentCreate
from app.services.company import CompanyService


class RiskAssessmentService:
    """Provide company-scoped assessment history, creation, and summaries."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._companies = CompanyService(session)
        self._repository = RiskAssessmentRepository(session)

    def list_for_company(self, company_id: int) -> list[dict[str, Any]]:
        """Return history for an existing company."""
        self._companies.get_company(company_id)
        return self._repository.list_for_company(company_id)

    def create_for_company(
        self,
        company_id: int,
        assessment: RiskAssessmentCreate,
    ) -> dict[str, Any]:
        """Create and return an assessment for an existing company."""
        self._companies.get_company(company_id)
        created = self._repository.create_for_company(company_id, assessment)
        self._session.commit()
        return created

    def get_summary(self, company_id: int) -> dict[str, Any]:
        """Return the current risk summary for an existing company."""
        company = self._companies.get_company(company_id)
        return self._repository.get_summary(company_id, str(company["company_name"]))
