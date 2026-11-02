"""Application logic for company-scoped market and evidence reads."""

from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.core.errors import APIError
from app.repositories.company import CompanyRepository
from app.repositories.market_data import MarketDataRepository
from app.services.company import CompanyNotFoundError


class MarketDataService:
    """Provide read operations over the existing market/evidence schema."""

    def __init__(self, session: Session) -> None:
        self._companies = CompanyRepository(session)
        self._repository = MarketDataRepository(session)

    def _require_company(self, company_id: int) -> None:
        if self._companies.get_company(company_id) is None:
            raise CompanyNotFoundError

    def _require_company_security(self, company_id: int, security_id: int) -> None:
        if self._repository.get_security_for_company(company_id, security_id) is None:
            raise APIError(
                404,
                "SECURITY_NOT_FOUND",
                f"Security with ID {security_id} was not found for company {company_id}.",
            )

    def get_company_securities(
        self,
        company_id: int,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return securities for an existing company."""
        self._require_company(company_id)
        return self._repository.list_company_securities(
            company_id, active_only, limit, offset
        )

    def get_company_market_observations(
        self,
        company_id: int,
        security_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return market observations for an existing company."""
        self._require_company(company_id)
        if security_id is not None:
            self._require_company_security(company_id, security_id)
        return self._repository.list_company_market_observations(
            company_id, security_id, start_date, end_date, limit, offset
        )

    def get_company_events(
        self,
        company_id: int,
        event_type: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return financial events for an existing company."""
        self._require_company(company_id)
        return self._repository.list_company_events(
            company_id, event_type, start_date, end_date, limit, offset
        )

    def get_company_news(
        self,
        company_id: int,
        security_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return direct and security-associated articles for a company."""
        self._require_company(company_id)
        if security_id is not None:
            self._require_company_security(company_id, security_id)
        return self._repository.list_company_news(
            company_id, security_id, start_date, end_date, limit, offset
        )
