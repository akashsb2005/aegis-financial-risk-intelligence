"""Database access for the existing companies table."""

from functools import lru_cache

from sqlalchemy import MetaData, Table, select
from sqlalchemy.orm import Session

from app.core.database import engine


@lru_cache(maxsize=1)
def _companies_table() -> Table:
    """Reflect the existing table instead of defining a duplicate schema."""
    return Table("companies", MetaData(), schema="public", autoload_with=engine)


class CompanyRepository:
    """Run read-only queries against the existing companies table."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._table = _companies_table()

    def list_companies(self, limit: int, offset: int) -> list[dict[str, object]]:
        """Return a deterministically ordered page of companies."""
        statement = (
            select(self._table)
            .order_by(self._table.c.company_id.asc())
            .limit(limit)
            .offset(offset)
        )
        rows = self._session.execute(statement).mappings().all()
        return [dict(row) for row in rows]

    def get_company(self, company_id: int) -> dict[str, object] | None:
        """Return one company by its primary key, if it exists."""
        statement = select(self._table).where(self._table.c.company_id == company_id)
        row = self._session.execute(statement).mappings().one_or_none()
        return dict(row) if row is not None else None
