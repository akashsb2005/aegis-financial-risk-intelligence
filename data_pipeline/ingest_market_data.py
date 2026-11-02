"""Fetch daily OHLCV history from Yahoo Finance and upsert into AEGIS.

Requires pre-existing rows in public.securities for every requested ticker.
This adapter is for educational/research use; review Yahoo Finance terms before use.
"""
from __future__ import annotations

import argparse
import os
from datetime import date
from decimal import Decimal
from typing import Any

import psycopg
import yfinance as yf


UPSERT_SQL = """
INSERT INTO public.market_observations
  (security_id, observation_date, open, high, low, close,
   adjusted_close, volume, source)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'yfinance')
ON CONFLICT (security_id, observation_date) DO UPDATE SET
  open = EXCLUDED.open,
  high = EXCLUDED.high,
  low = EXCLUDED.low,
  close = EXCLUDED.close,
  adjusted_close = EXCLUDED.adjusted_close,
  volume = EXCLUDED.volume,
  source = EXCLUDED.source,
  ingested_at = now()
"""


def as_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        if value != value:  # NaN
            return None
        return Decimal(str(value))
    except (ValueError, TypeError):
        return None


def ingest_ticker(conn: psycopg.Connection, ticker: str, start: str) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT security_id FROM public.securities
               WHERE ticker = %s AND is_active = TRUE""",
            (ticker,),
        )
        rows = cur.fetchall()
    if len(rows) != 1:
        raise ValueError(
            f"Expected exactly one active security for ticker {ticker!r}; found {len(rows)}"
        )
    security_id = rows[0][0]

    # Explicitly disable auto-adjust so Close and Adj Close remain distinct.
    history = yf.Ticker(ticker).history(start=start, auto_adjust=False, actions=False)
    if history.empty:
        raise ValueError(f"No historical observations returned for {ticker!r}")

    records = []
    for timestamp, row in history.iterrows():
        day: date = timestamp.date()
        close = as_decimal(row.get("Close"))
        if close is None:
            continue
        volume_value = row.get("Volume")
        volume = int(volume_value) if volume_value is not None and volume_value == volume_value else None
        records.append((
            security_id, day, as_decimal(row.get("Open")),
            as_decimal(row.get("High")), as_decimal(row.get("Low")),
            close, as_decimal(row.get("Adj Close")), volume,
        ))

    if not records:
        raise ValueError(f"No valid closing prices found for {ticker!r}")
    with conn.cursor() as cur:
        cur.executemany(UPSERT_SQL, records)
    conn.commit()
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tickers", nargs="+", required=True, help="Yahoo Finance ticker symbols")
    parser.add_argument("--start", default="2020-01-01", help="Inclusive start date (YYYY-MM-DD)")
    args = parser.parse_args()
    dsn = os.environ.get("AEGIS_PG_DSN")
    if not dsn:
        raise SystemExit("Set AEGIS_PG_DSN to a PostgreSQL connection string.")
    with psycopg.connect(dsn) as conn:
        for ticker in args.tickers:
            count = ingest_ticker(conn, ticker, args.start)
            print(f"{ticker}: upserted {count} daily observations")


if __name__ == "__main__":
    main()
