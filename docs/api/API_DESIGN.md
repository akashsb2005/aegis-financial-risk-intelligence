# AEGIS API

## 1. Implementation status

The FastAPI application under `backend/app/` mounts its implemented JSON API at `/api/v1` and accesses PostgreSQL through SQLAlchemy services and repositories. Pydantic schemas and FastAPI validation define request and response shapes. Expected application errors use an `error` object; some resource-not-found handlers return this envelope directly.

This is an implementation reference, not a promise that every project capability exists. Read-only APIs expose rows in the existing market/evidence tables. Live news/event ingestion, ML inference, semantic retrieval, evidence-grounded explanations, and deployment services are not implemented API capabilities.

## 2. Authentication and authorization

- Login issues an opaque bearer token for a server-managed session; the database stores a hash of the token.
- Company, financial-record, risk-read, and audit-history routes require an authenticated session. Read access is available to any authenticated role.
- Creating a risk assessment requires the `ANALYST` role. The assessor ID is taken from the authenticated identity, not trusted from the request body.
- Registration assigns new accounts the `ANALYST` role; logout revokes the current session.
- Password-reset requests return a generic acknowledgement. A reset token may be included only when development configuration explicitly enables it; reset confirmation validates the supplied token.
- The frontend stores its session token in browser `sessionStorage`, not an HttpOnly cookie.

## 3. Implemented endpoints

All paths below are relative to `/api/v1`.

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/health` | Public | Check API process responsiveness |
| GET | `/health/db` | Public | Check PostgreSQL connectivity |
| POST | `/auth/register` | Public | Register an ANALYST account |
| POST | `/auth/login` | Public | Authenticate and create a session |
| POST | `/auth/logout` | Authenticated | Revoke the current session |
| POST | `/auth/password-reset/request` | Public | Request reset without disclosing account existence |
| POST | `/auth/password-reset/confirm` | Public, token-validated | Consume a valid reset token and change the password |
| GET | `/companies` | Authenticated | List companies; `limit` 1–100 (default 20), `offset` >= 0 |
| GET | `/companies/{company_id}` | Authenticated | Retrieve one company |
| GET | `/companies/{company_id}/financial-records` | Authenticated | Retrieve a company's financial records |
| GET | `/companies/{company_id}/risk-assessments` | Authenticated | Retrieve historical risk assessments |
| POST | `/companies/{company_id}/risk-assessments` | ANALYST role | Create an assessment through the database procedure |
| GET | `/companies/{company_id}/risk-summary` | Authenticated | Retrieve the current risk summary |
| GET | `/companies/{company_id}/audit-history` | Authenticated | Retrieve company-scoped audit snapshots |
| GET | `/companies/{company_id}/risk-audit-history` | Authenticated | Retrieve company-scoped audit snapshots; `limit` 1–100 (default 50), `offset` >= 0 |
| GET | `/companies/{company_id}/securities` | Authenticated | List company securities; `active_only` defaults true; `limit` 1–100 (default 100), `offset` >= 0 |
| GET | `/companies/{company_id}/market-observations` | Authenticated | List company OHLCV observations; optional `security_id`, `start_date`, `end_date`; `limit` 1–100 (default 50), `offset` >= 0 |
| GET | `/companies/{company_id}/events` | Authenticated | List financial events; optional `event_type`, `start_date`, `end_date`; `limit` 1–100 (default 50), `offset` >= 0 |
| GET | `/companies/{company_id}/news` | Authenticated | List directly or security-associated articles; optional `security_id`, publication `start_date`, `end_date`; `limit` 1–100 (default 50), `offset` >= 0 |

Both audit-history routes read trigger-generated rows from the existing `risk_assessment_audit` table. `/audit-history` returns the full collection; `/risk-audit-history` supports bounded pagination. Neither creates a second audit store or changes the database schema.

Market reads use the existing `securities`, `market_observations`, `financial_events`, and `news_articles` tables created by `database/ddl/02_market_evidence.sql`; apply that migration after the core schema before using these routes. Market observations are joined through company-owned securities; news includes direct company associations and articles whose associated security belongs to the company. Supplying a security ID that is not owned by the requested company returns `404 SECURITY_NOT_FOUND`. All collection reads are bounded and deterministically ordered.

The market endpoints return JSON arrays. Security responses include security ID, company ID, ticker, exchange, asset type, currency, active status, and creation time. Observation responses include security/ticker/exchange, observation date, OHLC/adjusted-close values, volume, source, and ingestion time. Event responses include event type/date, title, description, source attribution, publication time, and creation time. News responses include company/security IDs, title/content, source attribution, publication time, and ingestion time. Empty collections return `200 OK` with `[]`.

All four market endpoints require an authenticated session and allow any authenticated role to read. Invalid pagination, dates, date ranges (`start_date > end_date`), or non-positive security IDs return FastAPI `422` validation responses. A positive security ID that is not owned by the requested company returns `404 SECURITY_NOT_FOUND`; missing companies return `404 COMPANY_NOT_FOUND`. News date filters compare the UTC publication date inclusively. The endpoints do not populate market/evidence tables or expose model predictions.

## 4. Resource and audit behavior

Company details and company-scoped collections verify that the company exists; missing companies return `404 COMPANY_NOT_FOUND`. Existing companies with no financial, risk, audit, or market/evidence rows return an empty array for collection routes.

Risk-assessment creation requires an authenticated ANALYST and calls the existing PostgreSQL `add_risk_assessment` procedure through the service layer. The existing database `AFTER INSERT` trigger copies the assessment into `risk_assessment_audit`. Audit reads return the persisted snapshot fields: audit ID, source assessment ID, company ID, score, log timestamp, action type, risk level, model version, explanation, and assessor ID.

Risk assessments remain append-only under the existing database trigger. The API does not change the schema or trigger behavior.

## 5. Status and error conventions

- `200 OK`: successful reads and operations
- `201 Created`: successful registration or assessment creation
- `400 Bad Request`: invalid or expired password-reset token
- `401 Unauthorized`: missing, invalid, expired, or revoked authentication
- `403 Forbidden`: authenticated user lacks the required role
- `404 Not Found`: requested company does not exist (`COMPANY_NOT_FOUND`) or requested security is not owned by that company (`SECURITY_NOT_FOUND`)
- `409 Conflict`: account email is already registered
- `422 Unprocessable Entity`: path, query, or request-schema validation failure
- `500 Internal Server Error`: unexpected server-side failure

Application errors may use this response shape:

```json
{
  "error": {
    "code": "COMPANY_NOT_FOUND",
    "message": "Company with ID 123 was not found."
  }
}
```

## 6. Implemented source locations

| Concern | Source |
|---|---|
| FastAPI application and exception handler | `backend/app/main.py` |
| Versioned routes | `backend/app/api/__init__.py` |
| Authentication and role dependencies | `backend/app/core/auth.py` |
| Authentication services | `backend/app/services/auth.py` |
| Risk-assessment and audit services | `backend/app/services/risk_assessment.py` |
| Market/evidence response schemas | `backend/app/schemas/market_data.py` |
| Market/evidence reads | `backend/app/repositories/market_data.py`, `backend/app/services/market_data.py` |
| Request/response schemas | `backend/app/schemas/` |
| API integration tests | `backend/tests/` |

## 7. Not yet implemented

Market/evidence ingestion and search, ML anomaly or risk inference, complete pgvector/semantic retrieval, and evidence-grounded AI explanation routes are not currently implemented. The read APIs do not include `model_predictions`. Do not describe these capabilities as operational API features.
