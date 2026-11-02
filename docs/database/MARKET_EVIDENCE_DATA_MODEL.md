# Market and evidence data model

This migration extends the existing AEGIS company/financial-record schema; it does not replace the original schema dump. Apply `database/ddl/02_market_evidence.sql` after `01_schema.sql`.

## Relations

- **securities** maps a traded instrument to an existing company. Exchange plus ticker is the natural unique key; a ticker alone is not globally unique.
- **market_observations** stores one daily OHLCV observation per security and date. Prices are non-negative, volume is non-negative, and OHLC ranges are checked.
- **financial_events** stores dated, sourced company events. A source URI is unique when supplied.
- **news_articles** stores sourced article text and must be associated with a company or security.
- **model_predictions** stores model outputs with model identity/version, prediction date, optional target date, feature/metric JSON and an optional signal.

## Data integrity and provenance

Market rows are unique by (security_id, observation_date), making repeat ingestion idempotent with an upsert. Every market row records its source and ingestion timestamp. Article/event source links are retained for provenance. Do not treat demo seed data as real market observations.

## Migration order

1. Apply `database/ddl/01_schema.sql`.
2. Apply `database/ddl/02_market_evidence.sql`.
3. Insert company master records, then securities referencing those company IDs.
4. Run the market-data ingestion script for those securities.

## Current boundary

This migration creates storage only. It does not claim that a live feed, event/news crawler, trained model, vector embedding, or AI explanation is already running. Those are separate implementation phases. The optional pgvector script remains a separate prerequisite until the embedding model and retrieval path are integrated.
