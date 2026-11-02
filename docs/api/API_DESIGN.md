# AEGIS API

## 1. Implementation status

The API described here is implemented in the FastAPI application under `backend/app/`. The versioned routes use `/api/v1`; JSON validation and response serialization are provided by Pydantic. Expected application errors use an `error` object containing a stable code and message. FastAPI request-validation failures use its standard `422` response.

The API connects to the existing PostgreSQL schema. It does not implement ML inference, news/event ingestion, vector retrieval, RAG, or deployment services.

## 2. Authentication and authorization

- Login issues an opaque bearer token for a server-managed session. The database stores a hash of the token, and the frontend keeps the active token in browser `sessionStorage`.
- Company, financial-record, risk-read, and audit-history routes require a valid authenticated session. These reads are available to any authenticated role.
- Creating a risk assessment requires the `ANALYST` role. The API assigns the assessor from the authenticated identity rather than trusting the request's `assessed_by` value.
- Registration assigns new accounts the `ANALYST` role.
- Password-reset requests return a generic acknowledgement. A reset token may be included only when the configured development environment explicitly enables that behavior.

## 3. Implemented endpoints

All paths below are relative to `/api/v1`.

| Method | Endpoint | Authentication | Behavior |
|---|---|---|---|
| POST | `/auth/register` | Public | Register an ANALYST account |
| POST | `/auth/login` | Public | Validate credentials and create a bearer session |
| POST | `/auth/logout` | Authenticated | Revoke the current session |
| POST | `/auth/password-reset/request` | Public | Request reset instructions without disclosing account existence |
| POST | `/auth/password-reset/confirm` | Public | Consume a valid reset token and change the password |
| GET | `/health` | Public | Check API process responsiveness |
| GET | `/health/db` | Public | Check database connectivity |
| GET | `/companies` | Authenticated | List companies; supports `limit` (default 20, maximum 100) and `offset` (default 0) |
| GET | `/companies/{company_id}` | Authenticated | Return one company |
| GET | `/companies/{company_id}/financial-records` | Authenticated | List a company's financial records |
| GET | `/companies/{company_id}/risk-assessments` | Authenticated | List a company's assessment history |
| POST | `/companies/{company_id}/risk-assessments` | ANALYST | Create an assessment through the existing PostgreSQL procedure |
| GET | `/companies/{company_id}/risk-summary` | Authenticated | Return current risk information from the existing database view |
| GET | `/companies/{company_id}/audit-history` | Authenticated | Return the company's persisted `risk_assessment_audit` records |

Company-scoped reads return `404 COMPANY_NOT_FOUND` when the company does not exist. Existing companies with no financial, risk, or audit rows return an empty array for collection routes. The audit-history response includes the audit ID, source assessment ID, company ID, risk score and level, timestamp, action type, model version, explanation, and assessor ID when present.

## 4. Data and audit flow

Risk-assessment creation is performed by an authenticated ANALYST. The application supplies the authenticated user ID as `assessed_by` and invokes the existing PostgreSQL procedure. The database's `AFTER INSERT` trigger writes the corresponding snapshot to `risk_assessment_audit`. The audit-history endpoint reads those persisted rows; it does not synthesize audit records from the assessment-history response.

Risk assessments remain append-only under the existing database trigger. The API does not change the schema or the database's audit behavior.

## 5. Error and status behavior

- `200 OK`: successful reads and completed operations
- `201 Created`: account registration and risk-assessment creation
- `400 Bad Request`: invalid or expired password-reset token
- `401 Unauthorized`: missing, invalid, expired, or revoked session where authentication is required
- `403 Forbidden`: authenticated user lacks the required role for assessment creation
- `404 Not Found`: requested company does not exist
- `409 Conflict`: account email is already registered
- `422 Unprocessable Entity`: request validation failure
- `500 Internal Server Error`: unexpected server failure

Expected application errors use the response shape:

```json
{
  "error": {
    "code": "COMPANY_NOT_FOUND",
    "message": "Company with ID 123 was not found."
  }
}
```

## 6. Future work

Model inference, live news/event ingestion, production pgvector integration, evidence retrieval/RAG, and production deployment are not implemented API capabilities. They remain future work and are not represented as operational endpoints.
