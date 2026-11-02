# AEGIS API Design

## 1. Status and scope

This document describes the FastAPI routes currently implemented in `backend/app`. The versioned router is mounted at `/api/v1`. The API is backed by PostgreSQL through SQLAlchemy services and repositories.

This is an implementation reference, not a promise that every proposed AEGIS feature exists. Market-price, news/event ingestion, ML inference, semantic retrieval, and AI-explanation routes are not currently implemented.

## 2. Conventions

- Base path: `/api/v1`.
- Request/response format: JSON.
- Authentication: bearer token for protected routes, backed by server-managed sessions.
- Authorization: authenticated-user dependency for read operations; the risk-assessment creation route additionally requires the `ANALYST` role.
- Pagination: `limit` and `offset` where supported.
- Validation: Pydantic request/response schemas, FastAPI path/query validation, and PostgreSQL constraints.
- Error responses may use the API error envelope `{"error":{"code":"...","message":"..."}}`; some resource-not-found handlers return this envelope directly.

## 3. Implemented endpoints

All paths below are relative to `/api/v1`.

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/health` | Public | Check API process responsiveness |
| GET | `/health/db` | Public | Check PostgreSQL connectivity |
| POST | `/auth/register` | Public | Register an ANALYST account |
| POST | `/auth/login` | Public | Authenticate and create a session |
| POST | `/auth/logout` | Authenticated | Revoke the current session |
| POST | `/auth/password-reset/request` | Public | Request a password-reset flow without disclosing account existence |
| POST | `/auth/password-reset/confirm` | Public, token-validated | Consume a valid reset token and change the password |
| GET | `/companies` | Authenticated | List companies; `limit` 1–100 (default 20), `offset` >= 0 |
| GET | `/companies/{company_id}` | Authenticated | Retrieve one company |
| GET | `/companies/{company_id}/financial-records` | Authenticated | Retrieve a company's financial records |
| GET | `/companies/{company_id}/risk-assessments` | Authenticated | Retrieve historical risk assessments |
| POST | `/companies/{company_id}/risk-assessments` | ANALYST role | Create an assessment through the database procedure |
| GET | `/companies/{company_id}/risk-summary` | Authenticated | Retrieve the current risk summary |
| GET | `/companies/{company_id}/risk-audit-history` | Authenticated | Retrieve trigger-generated audit snapshots; `limit` 1–100 (default 50), `offset` >= 0 |

The audit-history endpoint reads the existing `risk_assessment_audit` table; it does not create a second audit store or change the database schema.

## 4. Authentication and authorization

- Registration creates an account with the `ANALYST` role.
- Login validates credentials and creates a server-managed session.
- Protected routes use the authenticated-user dependency.
- Creating a risk assessment additionally uses the `ANALYST` role dependency.
- The assessor ID for a new risk assessment is taken from the authenticated user, not trusted from the request body.
- Logout revokes the current authenticated session.
- Password-reset request and confirmation are implemented as separate routes; reset tokens are validated by the authentication service.
- Do not expose password hashes, reset-token hashes, or session-token hashes in API responses.

The current frontend stores its session token in browser `sessionStorage`; it is not an HttpOnly-cookie design. See the README security limitation.

## 5. Resource behavior

### Company and financial records

Company listing supports pagination. Company details and financial records are scoped by company ID. A missing company is returned as `404` with code `COMPANY_NOT_FOUND`.

### Risk assessments

The read endpoints expose the current summary and assessment history. Creation requires the ANALYST role and calls the existing PostgreSQL `add_risk_assessment` procedure through the service layer. The authenticated user's ID is assigned as `assessed_by`.

### Risk audit history

`GET /companies/{company_id}/risk-audit-history?limit=50&offset=0` returns snapshots written by the database audit trigger. Results are company-scoped and ordered newest first by log timestamp and audit identifier. Pagination is bounded to a maximum page size of 100. Missing companies return `404`.

## 6. Status and error conventions

The implemented routes use standard HTTP status semantics, including:

- `200 OK`: successful read or operation.
- `201 Created`: successful registration or assessment creation.
- `401 Unauthorized`: missing or invalid authentication.
- `403 Forbidden`: authenticated user lacks the required role.
- `404 Not Found`: requested company does not exist.
- `422 Unprocessable Entity`: path, query, or request-schema validation failure.
- `500 Internal Server Error`: unexpected server-side failure.

Exact response schemas are defined in `backend/app/schemas/`; error behavior is implemented in the API handlers and exception handler. Consult those source files when changing the contract.

## 7. Implemented source locations

| Concern | Source |
|---|---|
| FastAPI application and exception handler | `backend/app/main.py` |
| Versioned routes | `backend/app/api/__init__.py` |
| Authentication and role dependencies | `backend/app/core/auth.py` |
| Authentication services | `backend/app/services/auth.py` |
| Company services | `backend/app/services/company.py` |
| Financial-record services | `backend/app/services/financial_record.py` |
| Risk-assessment and audit services | `backend/app/services/risk_assessment.py` |
| Request/response schemas | `backend/app/schemas/` |
| API integration tests | `backend/tests/` |

## 8. Not yet implemented

The following are project requirements or future integration work, not currently implemented API routes:

- Market price/volume history and securities endpoints.
- Financial event and news ingestion/search endpoints.
- ML anomaly detection and risk/volatility inference endpoints.
- Model-run metadata and prediction persistence beyond the current risk-assessment workflow.
- pgvector embedding and semantic retrieval endpoints.
- Evidence-grounded AI explanation endpoints.

Do not document these as operational until source code, tests, and runtime evidence are committed.
