# Market data ingestion

The script fetches daily OHLCV history through the `yfinance` Python package and upserts it into `public.market_observations`.

## Prerequisites

1. Apply `database/ddl/01_schema.sql` and then `database/ddl/02_market_evidence.sql`.
2. Insert the company master row and its security row. The ticker must be unique among active securities for this ingestion call.
3. Install `data_pipeline/requirements.txt`.
4. Set `AEGIS_PG_DSN` to a PostgreSQL DSN (for example `postgresql://USER:PASSWORD@localhost:5432/DBNAME`).

## Run

```powershell
pip install -r data_pipeline/requirements.txt
$env:AEGIS_PG_DSN = "postgresql://USER:PASSWORD@localhost:5432/DBNAME"
python data_pipeline/ingest_market_data.py --tickers AAPL MSFT --start 2020-01-01
```

The security rows must already exist and the ticker passed to the script must match exactly. For NSE symbols, use the Yahoo Finance symbol (for example, `RELIANCE.NS`) in the security master.

## Reproducibility and limitations

The provider is external and network-dependent; never make CI depend on a live Yahoo Finance request. Automated tests should use fixture data or mock the provider. The script sets `auto_adjust=False` explicitly and retains both Close and Adj Close. This is an educational/research adapter, not a guaranteed market-data SLA. Review Yahoo Finance terms and the yfinance project's personal-use restriction before use. Do not redistribute data without checking applicable terms.
