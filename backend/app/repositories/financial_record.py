"""Database access for the existing financial_records table."""

from functools import lru_cache

from sqlalchemy import MetaData, Table, select
from sqlalchemy.orm import Session

from app.core.database import engine


@lru_cache(maxsize=1)
def _financial_records_table() -> Table:
    """Reflect the existing table instead of defining a duplicate schema."""
    return Table(
        "financial_records",
        MetaData(),
        schema="public",
        autoload_with=engine,
    )


class FinancialRecordRepository:
    """Run read-only queries against the existing financial_records table."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._table = _financial_records_table()

    def list_for_company(self, company_id: int) -> list[dict[str, object]]:
        """Return a company's financial records in descending fiscal-year order."""
        statement = (
            select(self._table)
            .where(self._table.c.company_id == company_id)
            .order_by(
                self._table.c.fiscal_year.desc(),
                self._table.c.financial_record_id.desc(),
            )
        )
        rows = self._session.execute(statement).mappings().all()
        return [dict(row) for row in rows]
