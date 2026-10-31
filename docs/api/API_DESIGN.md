# AEGIS API Design

## 1. Status and scope

This document defines a proposed REST API boundary for the AEGIS application. The current tracked repository does not yet contain FastAPI source code; therefore, the endpoints below are a design contract, not a claim of implemented or tested routes.

## 2. Proposed conventions

- Base path: `/api/v1`
- Format: JSON over HTTPS
- Authentication: secure server-managed session or bearer-token mechanism
- Authorization: role-based access control
- Pagination: `limit` and `offset` for collection endpoints
- Errors: consistent JSON error envelope
- Database access: parameterized queries through a controlled service/repository layer

Example error envelope:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested company was not found."
  }
}
```

## 3. Proposed endpoints

| Method | Endpoint | Purpose | Database interaction |
|---|---|---|---|
| POST | `/auth/register` | Register an account | `users`, `roles` |
| POST | `/auth/login` | Authenticate user | `users`, `user_sessions` |
| POST | `/auth/logout` | Revoke current session | `user_sessions` |
| POST | `/auth/password-reset/request` | Create reset request | `password_reset_tokens` |
| POST | `/auth/password-reset/confirm` | Consume valid reset token | `password_reset_tokens`, `users` |
| GET | `/companies` | List companies | `companies` |
| GET | `/companies/{company_id}` | Company details | `companies` |
| GET | `/companies/{company_id}/financial-records` | Financial history | `financial_records` |
| GET | `/companies/{company_id}/risk-assessments` | Risk history | `risk_assessment` |
| POST | `/companies/{company_id}/risk-assessments` | Create assessment | `add_risk_assessment` / `risk_assessment` |
| GET | `/companies/{company_id}/risk-summary` | Latest risk summary | `company_risk_view` / risk functions |

## 4. Validation and authorization

- Validate path identifiers and request body types.
- Enforce score and risk-level constraints using both application validation and database constraints.
- Confirm that the target company exists before creating an assessment.
- Restrict administrative operations to authorized roles.
- Never accept a user ID or role from an untrusted client as proof of identity.
- Do not expose password hashes, reset-token hashes, or session-token hashes in API responses.
- Treat risk assessment history as append-only.

## 5. Example risk-assessment request

```json
{
  "risk_score": 72.5,
  "risk_level": "HIGH",
  "model_version": "baseline-1.0",
  "explanation": "Illustrative explanation; replace with a validated analysis.",
  "assessed_by": 1
}
```

The authenticated user identity should determine the assessor on the server; the example field is illustrative and should not be trusted directly from a client request.

## 6. Response and status conventions

- `200 OK`: successful read or update
- `201 Created`: resource created
- `204 No Content`: successful logout/revocation
- `400 Bad Request`: malformed input
- `401 Unauthorized`: missing or invalid authentication
- `403 Forbidden`: authenticated but not authorized
- `404 Not Found`: missing resource
- `409 Conflict`: uniqueness or state conflict
- `422 Unprocessable Entity`: validation failure
- `500 Internal Server Error`: unexpected server failure

## 7. Implementation and testing checklist

The future FastAPI implementation should include request/response schemas, dependency-based authentication, role checks, parameterized database access, transaction handling, structured errors, and automated endpoint tests.

No endpoint in this document should be described as operational until its implementation and runtime tests are available in the repository.
