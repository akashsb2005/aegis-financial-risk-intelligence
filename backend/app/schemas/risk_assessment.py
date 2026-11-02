"""Risk-assessment request and response schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class RiskAssessmentCreate(BaseModel):
    """Validated request body for creating an assessment."""

    risk_score: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("100"), max_digits=5, decimal_places=2),
    ]
    risk_level: RiskLevel
    model_version: Annotated[str | None, Field(max_length=50)] = None
    explanation: str | None = None
    assessed_by: int | None = None


class RiskAssessmentResponse(BaseModel):
    """Public representation of a risk-assessment row."""

    model_config = ConfigDict(from_attributes=True)

    risk_assessment_id: int
    company_id: int
    risk_score: Decimal
    risk_level: RiskLevel
    assessed_at: datetime
    model_version: str | None
    explanation: str | None
    assessed_by: int | None


class RiskSummaryResponse(BaseModel):
    """Current risk details for a company, if an assessment exists."""

    company_id: int
    company_name: str
    current_risk_level: RiskLevel | None
    current_risk_score: Decimal | None
    assessed_at: datetime | None
    model_version: str | None
