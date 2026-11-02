"""Application logic for financial-record queries."""

from sqlalchemy.orm import Session

from app.repositories.company import CompanyRepository
from app.repositories.financial_record import FinancialRecordRepository
from app.services.company import CompanyNotFoundError


class FinancialRecordService:
    """Provide financial-record operations using repository-layer queries."""

    def __init__(self, session: Session) -> None:
        self._companies = CompanyRepository(session)
        self._financial_records = FinancialRecordRepository(session)

    def list_for_company(self, company_id: int) -> list[dict[str, object]]:
        """Return records for an existing company, or raise if it is missing."""
        if self._companies.get_company(company_id) is None:
            raise CompanyNotFoundError
        return self._financial_records.list_for_company(company_id)
