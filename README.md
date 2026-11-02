# AEGIS — Financial Risk & Event Intelligence Platform

AEGIS is a database-centric financial risk intelligence project built around PostgreSQL, a FastAPI backend, and a Next.js web application. The application supports account and session workflows, role-based access control, company monitoring, risk assessments, and financial-record viewing.

## Current implementation status

- **Backend:** FastAPI with PostgreSQL integration, authentication and session handling, role-based access control (RBAC), company, risk-assessment, and financial-record APIs.
- **Frontend:** Next.js App Router with React, TypeScript, and Tailwind CSS. Account registration, login/logout, a session-protected dashboard, company monitoring, risk-assessment summary/history, database audit-history display, and financial-record viewing are integrated with the FastAPI API.
- **Database:** PostgreSQL schema, synthetic demo data, analytical SQL portfolio, and database verification scripts are included.
- **Verification:** PostgreSQL CI validation passed for the audit-history API pull request. Earlier backend tests (26 passed) and a frontend production build were verified for the application baseline; see [verification](#verification-boundary). The full suite/build should be rerun after subsequent application changes.
- **Not completed:** The two required trained/evaluated ML models, financial event/news ingestion, full pgvector embedding and semantic-retrieval integration, and evidence-grounded AI explanations. These remain active project work.

## Repository contents

| Path | Purpose |
|---|---|
| `frontend/` | Next.js App Router application; see [frontend setup](frontend/README.md) |
| `backend/` | FastAPI application, versioned routes, schemas, and service/repository layers |
| `database/ddl/01_schema.sql` | PostgreSQL schema dump: extensions, tables, constraints, sequences, routines, and triggers |
| `database/queries/01_basic_queries.sql` | Filtering, sorting, NULL handling, and basic aggregation |
| `database/queries/02_joins_and_aggregations.sql` | Joins, grouping, aggregate functions, and HAVING |
| `database/queries/03_subqueries_ctes_window_functions.sql` | Subqueries, CTEs, and window functions |
| `database/seeds/01_demo_data.sql` | Repeatable synthetic companies, financial records, analyst, and risk assessments |
| `database/verification/01_schema_verification.sql` | Read-only schema/catalog verification |
| `database/verification/02_behavioral_integration_tests.sql` | Trigger, append-only, and CHECK-constraint behavior tests |
| `database/verification/03_transaction_demo.sql` | COMMIT, SAVEPOINT rollback, and full ROLLBACK demonstrations |
| `database/verification/04_final_structure_assertions.sql` | Fail-fast assertions for required tables, constraints, triggers, view, routines, and index |
| `database/verification/05_concurrency_demo.sh` | Two-session row-locking, SELECT FOR UPDATE, and REPEATABLE READ demonstration |
| `database/vector/01_pgvector_evidence.sql` | Optional pgvector evidence-retrieval migration and sample queries |
| `docs/PROJECT_REQUIREMENTS.md` | Project scope and requirements |
| `docs/database/DATABASE_DESIGN.md` | Database design overview |
| `docs/database/ER_DESIGN.md` | ER model and relationship documentation |
| `docs/database/RELATIONAL_SCHEMA.md` | Relations, keys, constraints, indexes, and routines |
| `docs/database/DATA_DICTIONARY.md` | Attribute-level data dictionary |
| `docs/database/FUNCTIONAL_DEPENDENCIES.md` | Functional-dependency analysis |\n| `docs/database/ATTRIBUTE_CLOSURE_ANALYSIS.md` | Step-by-step attribute closures and candidate-key calculations |
| `docs/database/NORMALIZATION.md` | 1NF, 2NF, 3NF, and BCNF assessment |
| `docs/database/SYSTEM_ARCHITECTURE.md` | Current implementation boundary and proposed architecture |
| `docs/api/API_DESIGN.md` | Implemented FastAPI endpoints, access rules, and known API gaps |
| `docs/ml/ML_DESIGN.md` | ML workflow, target design, evaluation, and completion criteria |
| `docs/TEAM_CONTRIBUTION.md` | Team roles and contribution record |

## Database setup

The schema targets PostgreSQL 18.x and enables the `pgcrypto` extension. Create a database, connect to it, and apply `database/ddl/01_schema.sql` using a PostgreSQL client that supports the commands emitted by `pg_dump`.

The dump contains database objects, not a portable guarantee of application users, passwords, or production secrets. Configure database roles and credentials separately for each environment. Never commit real credentials.

## Environment variables

- **Backend:** Set `AEGIS_DATABASE_URL` to the SQLAlchemy PostgreSQL URL for the application database. The backend reads settings from `backend/.env` or the repository-root `.env`; `backend/.env.example` is a template. For example, replace every placeholder below with your own local values:

  ```text
  AEGIS_DATABASE_URL=postgresql+psycopg://<YOUR_USER>:<YOUR_PASSWORD>@localhost:5432/<YOUR_DATABASE>
  ```

- **Backend tests:** Set `AEGIS_TEST_DATABASE_URL` in the test process to a separate, disposable PostgreSQL database whose name contains `test` as a delimited component (for example, `aegis_test`). Apply the project schema to it before running tests. Tests require this explicit setting and do not fall back to the application database.
- **Frontend:** Create `frontend/.env.local` from `frontend/.env.example` and set `NEXT_PUBLIC_API_BASE_URL` to the FastAPI v1 base URL. The local default is `http://localhost:8000/api/v1`.

Do not commit `.env`, `.env.local`, passwords, tokens, or API keys. Use placeholders in shared documentation and keep real credentials in local environment files.

## FastAPI backend setup and run

1. Create a PostgreSQL database and apply `database/ddl/01_schema.sql` as described above.
2. From the repository root, create and activate a virtual environment and install the backend and test dependencies:

   ```powershell
   python -m venv backend\.venv
   .\backend\.venv\Scripts\Activate.ps1
   pip install -r backend\requirements.txt -r backend\requirements-dev.txt
   ```

3. Copy `backend\.env.example` to `backend\.env` and set `AEGIS_DATABASE_URL` to your application database URL.
4. Start the API from the repository root:

   ```powershell
   uvicorn app.main:app --app-dir backend --reload
   ```

   The API is available at `http://localhost:8000`; its versioned routes use `/api/v1`. The health check is `GET http://localhost:8000/api/v1/health`.

## Next.js frontend setup and run

The frontend requires the FastAPI backend and PostgreSQL database to be configured and running. From the `frontend` directory:

```powershell
npm ci
Copy-Item .env.example .env.local
```

Set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1` in `.env.local` (or use the URL for your backend), then start the development server:

```powershell
npm run dev
```

Open `http://localhost:3000`. The frontend rewrites its `/api/v1` requests to the configured API base URL.

## Application verification commands

### Backend application tests

Prepare the separate PostgreSQL test database described under [environment variables](#environment-variables), then set its URL in the PowerShell session before running the tests from the repository root:

```powershell
$env:AEGIS_TEST_DATABASE_URL = "postgresql+psycopg://<YOUR_USER>:<YOUR_PASSWORD>@localhost:5432/aegis_test"
pytest -q backend/tests
```

The currently verified result is **26 passed**.

### Frontend production build

From the `frontend` directory, install dependencies if needed and run:

```powershell
npm ci
npm run build
```

The current production build has been verified successfully.

## SQL learning / evaluation portfolio

Run the three query files in numeric order after applying the schema. They are read-only analytical examples and cover:
- SELECT, WHERE, ORDER BY, LIMIT, NULL handling
- INNER JOIN and LEFT JOIN
- COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING
- Scalar, correlated, IN, EXISTS, and NOT EXISTS subqueries
- Common table expressions (CTEs)
- ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, and running aggregates

The query files are examples. Run `database/seeds/01_demo_data.sql` first to load deterministic synthetic demonstration data; it is safe to execute repeatedly and uses no real personal or financial data.

## Important database behavior

- Risk assessments are historical records. The schema includes a trigger that rejects UPDATE and DELETE operations on the risk-assessment table.
- An AFTER INSERT trigger copies assessment details into the audit table.
- The audit table's source identifiers are not declared foreign keys in the tracked DDL; they are copied by the trigger.
- The core database schema does not define news or event tables. An optional, separate pgvector migration and similarity-search examples are provided in `database/vector/01_pgvector_evidence.sql`; this requires pgvector to be installed and a real embedding model selected. It is not part of the core CI validation.

## Verification boundary

GitHub Actions provisions a disposable PostgreSQL 18 instance, applies the schema, loads the synthetic seed data, executes the analytical query portfolio, runs read-only catalog verification, and executes behavioral integration tests, transaction demonstrations, structural assertions, and a two-session concurrency/isolation demonstration. This is genuine automated database execution evidence; it is not a screenshot of a local database client or proof of an end-to-end web application. See the [PostgreSQL validation workflow](.github/workflows/postgres-validation.yml) and [workflow runs](https://github.com/akashsb2005/aegis-financial-risk-intelligence/actions).

## Application Demonstration Evidence

Genuine screenshots captured from the running AEGIS application during local PostgreSQL/FastAPI/Next.js integration verification:

- [Company Monitoring](https://chatgpt.com/c/docs/evidence/01_company_monitoring.png)
- [Financial Records](https://chatgpt.com/c/docs/evidence/02_financial_records.png)
- [Risk Assessments](https://chatgpt.com/c/docs/evidence/03_risk_assessments.png)

## Current limitations and future work

The project does not currently include the two required trained and evaluated ML models, financial news/event ingestion, a complete pgvector embedding and semantic-retrieval workflow, or evidence-grounded AI explanations. These capabilities remain to be implemented and must not be presented as completed. Docker, cloud hosting, and production deployment are outside the agreed project scope. Frontend session tokens are currently held in browser `sessionStorage`, not an HttpOnly cookie; this is a current implementation limitation and is not a claim of production-grade authentication security.

## Team

See [Team Contributions](docs/TEAM_CONTRIBUTION.md) for the student details and responsibility split.
