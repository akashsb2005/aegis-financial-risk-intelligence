# Local Windows market-data and ML verification

This guide is for an existing local `aegis_db` with `02_market_evidence.sql` and `02_public_securities.sql` already applied. Do **not** reapply the full core schema to a populated database.

## 1. Verify your virtual environment

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\data_pipeline\requirements.txt -r .\ml\requirements.txt
python -c "import yfinance, psycopg, pandas, feedparser, sklearn, joblib; print('ALL DEPENDENCIES OK')"
```

## 2. Apply narrowly scoped market pipeline grants

A database administrator must run this **once** (safe to repeat):

```powershell
psql -U postgres -d aegis_db -v ON_ERROR_STOP=1 -f ".\database\permissions\01_market_pipeline_local.sql"
```

The administrator password is the `postgres` role password, **not** the `aegis_user` password. Type it only at the hidden password prompt. The script grants `aegis_user` SELECT access to `companies` and `securities`, and SELECT/INSERT/UPDATE on market observations, events, news, and predictions, plus the corresponding identity sequences. It does not grant DELETE or change core application table privileges.

If `psql` says `password authentication failed for user "postgres"`, verify the administrator password first. Do not repeatedly run the ingestion script; it cannot repair missing privileges.

## 3. Set the private connection string

In the **same** PowerShell session, enter your real password locally, never in Git or chat:

```powershell
$pw = Read-Host "Enter aegis_user database password"
$env:AEGIS_PG_DSN = "postgresql://aegis_user:$pw@localhost:5432/aegis_db"
Remove-Variable pw
```

The above URL form works only when the password contains URL-safe characters; percent-encode reserved characters if necessary. For an existing `AEGIS_PG_DSN`, you can skip this step.

Test the role's access:

```powershell
python -c "import os, psycopg; c=psycopg.connect(os.environ['AEGIS_PG_DSN']); print('securities:', c.execute('SELECT COUNT(*) FROM public.securities').fetchone()[0]); print('market rows:', c.execute('SELECT COUNT(*) FROM public.market_observations').fetchone()[0]); c.close()"
```

## 4. Ingest genuine historical data

```powershell
python .\data_pipeline\ingest_market_data.py --tickers AAPL MSFT NVDA TCS.NS RELIANCE.NS --start 2020-01-01
```

This contacts Yahoo Finance; data availability and rate limits depend on the external provider. Review the provider's terms. Never substitute fabricated prices for missing downloads.

Verify stored rows using the already-connected application role (no administrator password required):

```powershell
python -c "import os, psycopg; c=psycopg.connect(os.environ['AEGIS_PG_DSN']); print(*c.execute('SELECT s.ticker, COUNT(*), MIN(m.observation_date), MAX(m.observation_date) FROM public.market_observations m JOIN public.securities s USING (security_id) GROUP BY s.ticker ORDER BY s.ticker').fetchall(), sep='\n'); c.close()"
```

## 5. Train and persist model predictions

Only after enough real market observations are present:

```powershell
python -m ml.train_models
```

Training writes `ml/artifacts/volatility_model.joblib`, `ml/artifacts/anomaly_model.joblib`, and `ml/artifacts/metrics.json`, and upserts predictions into `public.model_predictions`. At least 100 usable feature rows are required; the first 20 or more sessions per security are used for rolling features. A chronological train/test split is used; metrics must be inspected rather than assumed.

Verify predictions:

```powershell
python -c "import os, psycopg; c=psycopg.connect(os.environ['AEGIS_PG_DSN']); print(*c.execute('SELECT prediction_type, COUNT(*) FROM public.model_predictions GROUP BY prediction_type ORDER BY prediction_type').fetchall(), sep='\n'); c.close()"
```

## 6. Start the API and UI

Install backend requirements in the active environment:

```powershell
python -m pip install -r .\backend\requirements.txt
```

Create `backend/.env` from `backend/.env.example` if missing and set `AEGIS_DATABASE_URL` to the SQLAlchemy variant `postgresql+psycopg://...`. Keep this file untracked. Start:

```powershell
uvicorn app.main:app --app-dir backend --reload
```

In a second terminal, from `frontend`:

```powershell
npm ci
if (!(Test-Path .env.local)) { Copy-Item .env.example .env.local }
npm run dev
```

Visit `http://localhost:8000/api/v1/health` and `http://localhost:3000`. Confirm authentication, company monitoring, and the prediction dashboard using real persisted records. These local checks cannot be inferred from passing CI tests.

## Boundaries

The optional pgvector migration requires the server-side pgvector extension. RSS feeds require an operator-supplied permitted feed URL. Evidence-grounded explanations and production deployment are not demonstrated by this quick-start procedure. Do not commit passwords, real session tokens, model artifacts, or local `.env` files.
