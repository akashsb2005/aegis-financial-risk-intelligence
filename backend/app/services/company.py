"""Application logic for company queries."""

from sqlalchemy.orm import Session

from app.repositories.company import CompanyRepository


class CompanyNotFoundError(Exception):
    """Raised when a requested company does not exist."""


class CompanyService:
    """Provide company operations using the repository layer."""

    def __init__(self, session: Session) -> None:
        self._repository = CompanyRepository(session)

    def list_companies(self, limit: int, offset: int) -> list[dict[str, object]]:
        """Return a paginated list of companies."""
        return self._repository.list_companies(limit, offset)

    def get_company(self, company_id: int) -> dict[str, object]:
        """Return a company or raise when its identifier is unknown."""
        company = self._repository.get_company(company_id)
        if company is None:
            raise CompanyNotFoundError
        return company
