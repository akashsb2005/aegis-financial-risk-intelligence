"""Response schemas for market and evidence data."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SecurityResponse(BaseModel):
    """Public representation of a company security."""

    model_config = ConfigDict(from_attributes=True)

    security_id: int
    company_id: int
    ticker: str
    exchange: str
    asset_type: str
    currency: str
    is_active: bool
    created_at: datetime


class MarketObservationResponse(BaseModel):
    """Public representation of one daily market observation."""

    model_config = ConfigDict(from_attributes=True)

    observation_id: int
    security_id: int
    ticker: str
    exchange: str
    observation_date: date
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal
    adjusted_close: Decimal | None
    volume: int | None
    source: str
    ingested_at: datetime


class FinancialEventResponse(BaseModel):
    """Public representation of one company financial event."""

    model_config = ConfigDict(from_attributes=True)

    event_id: int
    company_id: int
    event_type: str
    event_date: date
    title: str
    description: str | None
    source_name: str | None
    source_uri: str | None
    published_at: datetime | None
    created_at: datetime


class NewsArticleResponse(BaseModel):
    """Public representation of one sourced news article."""

    model_config = ConfigDict(from_attributes=True)

    article_id: int
    company_id: int | None
    security_id: int | None
    title: str
    content: str
    source_name: str
    source_uri: str
    published_at: datetime | None
    ingested_at: datetime
