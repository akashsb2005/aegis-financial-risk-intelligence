"""Database access for risk assessments and the existing risk summary view."""

from functools import lru_cache
from typing import Any

from sqlalchemy import MetaData, Table, select, text
from sqlalchemy.orm import Session

from app.core.database import engine
from app.schemas.risk_assessment import RiskAssessmentCreate


@lru_cache(maxsize=1)
def _risk_assessments_table() -> Table:
    """Reflect the existing risk_assessment table."""
    return Table(
        "risk_assessment",
        MetaData(),
        schema="public",
        autoload_with=engine,
    )


@lru_cache(maxsize=1)
def _company_risk_view() -> Table:
    """Reflect the existing company_risk_view."""
    return Table(
        "company_risk_view",
        MetaData(),
        schema="public",
        autoload_with=engine,
    )


class RiskAssessmentRepository:
    """Run database queries and the existing assessment procedure."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._assessments = _risk_assessments_table()
        self._risk_view = _company_risk_view()

    def list_for_company(self, company_id: int) -> list[dict[str, Any]]:
        """Return assessment history newest first."""
        statement = (
            select(self._assessments)
            .where(self._assessments.c.company_id == company_id)
            .order_by(
                self._assessments.c.assessed_at.desc(),
                self._assessments.c.risk_assessment_id.desc(),
            )
        )
        rows = self._session.execute(statement).mappings().all()
        return [dict(row) for row in rows]

    def create_for_company(
        self,
        company_id: int,
        assessment: RiskAssessmentCreate,
    ) -> dict[str, Any]:
        """Create through the database procedure and fetch this session's row."""
        self._session.execute(
            text(
                "CALL public.add_risk_assessment("
                ":company_id, :risk_score, :risk_level, :model_version, "
                ":explanation, :assessed_by)"
            ),
            {
                "company_id": company_id,
                "risk_score": assessment.risk_score,
                "risk_level": assessment.risk_level,
                "model_version": assessment.model_version,
                "explanation": assessment.explanation,
                "assessed_by": assessment.assessed_by,
            },
        )
        assessment_id = self._session.execute(
            text(
                "SELECT currval(pg_get_serial_sequence("
                "'public.risk_assessment', 'risk_assessment_id'))"
            )
        ).scalar_one()
        statement = select(self._assessments).where(
            self._assessments.c.risk_assessment_id == assessment_id
        )
        row = self._session.execute(statement).mappings().one()
        return dict(row)

    def get_summary(
        self,
        company_id: int,
        company_name: str,
    ) -> dict[str, Any]:
        """Return current risk details from the existing summary view."""
        statement = (
            select(self._risk_view)
            .where(self._risk_view.c.company_id == company_id)
            .order_by(
                self._risk_view.c.assessed_at.desc(),
                self._risk_view.c.risk_assessment_id.desc(),
            )
            .limit(1)
        )
        row = self._session.execute(statement).mappings().one_or_none()
        if row is None:
            return {
                "company_id": company_id,
                "company_name": company_name,
                "current_risk_level": None,
                "current_risk_score": None,
                "assessed_at": None,
                "model_version": None,
            }
        return {
            "company_id": row["company_id"],
            "company_name": row["company_name"],
            "current_risk_level": row["risk_level"],
            "current_risk_score": row["risk_score"],
            "assessed_at": row["assessed_at"],
            "model_version": row["model_version"],
        }
