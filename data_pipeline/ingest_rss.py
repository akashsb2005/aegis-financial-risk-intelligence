"""Ingest company-tagged RSS articles and event candidates into AEGIS.

Use feeds whose terms permit this use. The script stores source URLs and publication
timestamps; keyword-classified event rows are candidates for human review, not verified facts.
"""
from __future__ import annotations

import argparse
import calendar
import os
import re
from datetime import datetime, timezone
from typing import Any

import feedparser
import psycopg

EVENT_RULES = {
    "EARNINGS": ("earnings", "quarterly results", "annual results", "revenue guidance"),
    "MERGER_ACQUISITION": ("merger", "acquisition", "takeover", "acquire"),
    "DIVIDEND": ("dividend", "payout"),
    "REGULATORY": ("regulator", "regulatory", "antitrust", "investigation", "fine"),
    "LITIGATION": ("lawsuit", "litigation", "court filing", "settlement"),
    "BANKRUPTCY": ("bankruptcy", "insolvency", "liquidation"),
    "LEADERSHIP": ("appoints ceo", "resigns", "steps down", "chief executive"),
}


def classify_event(title: str, summary: str) -> str | None:
    text = f"{title} {summary}".casefold()
    for event_type, phrases in EVENT_RULES.items():
        if any(phrase in text for phrase in phrases):
            return event_type
    return None


def published_datetime(entry: Any) -> datetime | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc)


def ingest_feed(conn: psycopg.Connection, ticker: str, feed_url: str) -> tuple[int, int]:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT security_id, company_id FROM public.securities
               WHERE ticker = %s AND is_active = TRUE""",
            (ticker,),
        )
        matches = cur.fetchall()
    if len(matches) != 1:
        raise ValueError(f"Expected one active security for {ticker!r}; found {len(matches)}")
    security_id, company_id = matches[0]
    feed = feedparser.parse(feed_url)
    if getattr(feed, "bozo", False) and not feed.entries:
        raise ValueError(f"Could not parse RSS feed: {feed_url}")

    articles = events = 0
    with conn.cursor() as cur:
        for entry in feed.entries:
            source_uri = entry.get("link")
            title = (entry.get("title") or "").strip()
            summary = re.sub(r"<[^>]+>", " ", entry.get("summary", "")).strip()
            if not source_uri or not title:
                continue
            published_at = published_datetime(entry)
            cur.execute(
                """INSERT INTO public.news_articles
                   (company_id, security_id, title, content, source_name,
                    source_uri, published_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (source_uri) DO NOTHING
                   RETURNING article_id""",
                (company_id, security_id, title, summary or title,
                 feed.feed.get("title", "RSS feed"), source_uri, published_at),
            )
            inserted = cur.fetchone()
            if not inserted:
                continue
            articles += 1
            event_type = classify_event(title, summary)
            if event_type:
                event_date = published_at.date() if published_at else datetime.now(timezone.utc).date()
                cur.execute(
                    """INSERT INTO public.financial_events
                       (company_id, event_type, event_date, title, description,
                        source_name, source_uri, published_at)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                       ON CONFLICT (source_uri) DO NOTHING""",
                    (company_id, event_type, event_date, title, summary,
                     feed.feed.get("title", "RSS feed"), source_uri, published_at),
                )
                events += cur.rowcount
    conn.commit()
    return articles, events


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", required=True, help="Ticker already present in public.securities")
    parser.add_argument("--feed-url", required=True, help="RSS/Atom feed URL")
    args = parser.parse_args()
    dsn = os.environ.get("AEGIS_PG_DSN")
    if not dsn:
        raise SystemExit("Set AEGIS_PG_DSN to a PostgreSQL connection string.")
    with psycopg.connect(dsn) as conn:
        article_count, event_count = ingest_feed(conn, args.ticker, args.feed_url)
    print(f"{args.ticker}: inserted {article_count} articles and {event_count} event candidates")


if __name__ == "__main__":
    main()
