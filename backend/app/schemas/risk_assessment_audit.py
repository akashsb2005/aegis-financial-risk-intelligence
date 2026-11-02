"""Response schema for immutable risk-assessment audit snapshots."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.risk_assessment import RiskLevel


class RiskAssessmentAuditResponse(BaseModel):
    """Public representation of one database-generated audit snapshot."""

    model_config = ConfigDict(from_attributes=True)

    audit_id: int
    risk_assessment_id: int
    company_id: int
    risk_score: Decimal
    logged_at: datetime
    action_type: str
    risk_level: RiskLevel
    model_version: str | None
    explanation: str | None
    assessed_by: int | None
