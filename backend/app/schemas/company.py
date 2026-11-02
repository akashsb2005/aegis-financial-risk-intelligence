"""Company API response schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CompanyResponse(BaseModel):
    """Public representation of a company row."""

    model_config = ConfigDict(from_attributes=True)

    company_id: int
    company_name: str
    registration_number: str | None
    industry: str | None
    country: str | None
    annual_revenue: Decimal | None
    employee_count: int | None
    created_at: datetime
    updated_at: datetime
