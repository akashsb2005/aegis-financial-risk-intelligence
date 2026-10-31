"""Financial-record API response schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FinancialRecordResponse(BaseModel):
    """Public representation of a financial record row."""

    model_config = ConfigDict(from_attributes=True)

    financial_record_id: int
    company_id: int
    fiscal_year: int
    revenue: Decimal | None
    net_profit: Decimal | None
    total_assets: Decimal | None
    total_liabilities: Decimal | None
    total_debt: Decimal | None
    shareholders_equity: Decimal | None
    operating_cash_flow: Decimal | None
    created_at: datetime
