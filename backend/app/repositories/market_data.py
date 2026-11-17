"""Database access for the existing market/evidence tables."""

from datetime import date, datetime, time, timezone
from functools import lru_cache
from typing import Any

from sqlalchemy import MetaData, Table, or_, select
from sqlalchemy.orm import Session

from app.core.database import engine


@lru_cache(maxsize=1)
def _market_tables() -> tuple[Table, Table, Table, Table]:
    """Reflect the existing tables rather than defining a duplicate schema."""
    metadata = MetaData()
    securities = Table("securities", metadata, schema="public", autoload_with=engine)
    observations = Table(
        "market_observations", metadata, schema="public", autoload_with=engine
    )
    events = Table("financial_events", metadata, schema="public", autoload_with=engine)
    articles = Table("news_articles", metadata, schema="public", autoload_with=engine)
    return securities, observations, events, articles


def _utc_start(date_value: date) -> datetime:
    return datetime.combine(date_value, time.min, tzinfo=timezone.utc)


def _utc_end_inclusive(date_value: date) -> datetime:
    return datetime.combine(date_value, time.max, tzinfo=timezone.utc)


class MarketDataRepository:
    """Run read-only queries against the existing market/evidence tables."""

    def __init__(self, session: Session) -> None:
        self._session = session
        (
            self._securities,
            self._observations,
            self._events,
            self._articles,
        ) = _market_tables()

    def list_company_securities(
        self, company_id: int, active_only: bool, limit: int, offset: int
    ) -> list[dict[str, Any]]:
        """Return a bounded page of securities owned by the company."""
        statement = select(self._securities).where(
            self._securities.c.company_id == company_id
        )
        if active_only:
            statement = statement.where(self._securities.c.is_active.is_(True))
        statement = (
            statement.order_by(
                self._securities.c.exchange.asc(),
                self._securities.c.ticker.asc(),
                self._securities.c.security_id.asc(),
            )
            .limit(limit)
            .offset(offset)
        )
        return [dict(row) for row in self._session.execute(statement).mappings().all()]

    def get_security_for_company(
        self, company_id: int, security_id: int
    ) -> dict[str, Any] | None:
        """Return a security only when it belongs to the requested company."""
        statement = select(self._securities).where(
            self._securities.c.company_id == company_id,
            self._securities.c.security_id == security_id,
        )
        row = self._session.execute(statement).mappings().one_or_none()
        return dict(row) if row is not None else None

    def list_company_market_observations(
        self,
        company_id: int,
        security_id: int | None,
        start_date: date | None,
        end_date: date | None,
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        """Return market observations through securities owned by the company."""
        statement = (
            select(
                self._observations.c.observation_id,
                self._observations.c.security_id,
                self._securities.c.ticker,
                self._securities.c.exchange,
                self._observations.c.observation_date,
                self._observations.c.open,
                self._observations.c.high,
                self._observations.c.low,
                self._observations.c.close,
                self._observations.c.adjusted_close,
                self._observations.c.volume,
                self._observations.c.source,
                self._observations.c.ingested_at,
            )
            .select_from(
                self._observations.join(
                    self._securities,
                    self._observations.c.security_id == self._securities.c.security_id,
                )
            )
            .where(self._securities.c.company_id == company_id)
        )
        if security_id is not None:
            statement = statement.where(self._securities.c.security_id == security_id)
        if start_date is not None:
            statement = statement.where(
                self._observations.c.observation_date >= start_date
            )
        if end_date is not None:
            statement = statement.where(
                self._observations.c.observation_date <= end_date
            )
        statement = (
            statement.order_by(
                self._observations.c.observation_date.desc(),
                self._observations.c.observation_id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        return [dict(row) for row in self._session.execute(statement).mappings().all()]

    def list_company_events(
        self,
        company_id: int,
        event_type: str | None,
        start_date: date | None,
        end_date: date | None,
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        """Return a bounded page of events owned by the company."""
        statement = select(self._events).where(
            self._events.c.company_id == company_id
        )
        if event_type is not None:
            statement = statement.where(self._events.c.event_type == event_type)
        if start_date is not None:
            statement = statement.where(self._events.c.event_date >= start_date)
        if end_date is not None:
            statement = statement.where(self._events.c.event_date <= end_date)
        statement = (
            statement.order_by(
                self._events.c.event_date.desc(),
                self._events.c.event_id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        return [dict(row) for row in self._session.execute(statement).mappings().all()]

    def list_company_news(
        self,
        company_id: int,
        security_id: int | None,
        start_date: date | None,
        end_date: date | None,
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        """Return directly or security-associated articles for the company."""
        statement = (
            select(
                self._articles.c.article_id,
                self._articles.c.company_id,
                self._articles.c.security_id,
                self._articles.c.title,
                self._articles.c.content,
                self._articles.c.source_name,
                self._articles.c.source_uri,
                self._articles.c.published_at,
                self._articles.c.ingested_at,
            )
            .select_from(
                self._articles.outerjoin(
                    self._securities,
                    self._articles.c.security_id == self._securities.c.security_id,
                )
            )
            .where(
                or_(
                    self._articles.c.company_id == company_id,
                    self._securities.c.company_id == company_id,
                )
            )
        )
        if security_id is not None:
            statement = statement.where(self._articles.c.security_id == security_id)
        if start_date is not None:
            statement = statement.where(
                self._articles.c.published_at >= _utc_start(start_date)
            )
        if end_date is not None:
            statement = statement.where(
                self._articles.c.published_at <= _utc_end_inclusive(end_date)
            )
        statement = (
            statement.order_by(
                self._articles.c.published_at.desc().nulls_last(),
                self._articles.c.article_id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        return [dict(row) for row in self._session.execute(statement).mappings().all()]
