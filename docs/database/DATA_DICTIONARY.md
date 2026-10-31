# AEGIS Data Dictionary

This dictionary summarizes the attributes in the eight relations defined by `database/ddl/01_schema.sql`. NN = NOT NULL, PK = primary key, FK = foreign key, UQ = UNIQUE, CK = CHECK constraint.

## companies

| Attribute | Type | Constraint | Meaning |
|---|---|---|---|
| company_id | integer | PK, NN | Unique company identifier |
| company_name | varchar(200) | NN | Company name |
| registration_number | varchar(100) | UQ, nullable | Optional unique registration identifier |
| industry | varchar(100) | Nullable | Industry classification |
| country | varchar(100) | Nullable | Country |
| annual_revenue | numeric(18,2) | Nullable, CK >= 0 | Annual revenue |
| employee_count | integer | Nullable, CK >= 0 | Employee count |
| created_at | timestamp | NN, default CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | timestamp | NN, default CURRENT_TIMESTAMP | Update timestamp |

## financial_records

| Attribute | Type | Constraint | Meaning |
|---|---|---|---|
| financial_record_id | integer | PK, NN | Unique financial record |
| company_id | integer | FK, NN, ON DELETE CASCADE | Related company |
| fiscal_year | integer | NN, CK >= 1900 | Financial year |
| revenue | numeric(18,2) | Nullable, CK >= 0 | Revenue |
| net_profit | numeric(18,2) | Nullable | Net profit |
| total_assets | numeric(18,2) | Nullable, CK >= 0 | Total assets |
| total_liabilities | numeric(18,2) | Nullable, CK >= 0 | Total liabilities |
| total_debt | numeric(18,2) | Nullable, CK >= 0 | Total debt |
| shareholders_equity | numeric(18,2) | Nullable | Shareholders' equity |
| operating_cash_flow | numeric(18,2) | Nullable | Operating cash flow |
| created_at | timestamp | NN, default CURRENT_TIMESTAMP | Creation timestamp |

Additional constraint: UNIQUE(company_id, fiscal_year).

## roles

| Attribute | Type | Constraint | Meaning |
|---|---|---|---|
| role_id | integer | PK, NN | Unique role identifier |
| role_name | varchar(50) | NN, UQ | Unique role name |
| description | text | Nullable | Role description |
| created_at | timestamp | NN, default CURRENT_TIMESTAMP | Creation timestamp |

## users

| Attribute | Type | Constraint | Meaning |
|---|---|---|---|
| user_id | integer | PK, NN | Unique user identifier |
| role_id | integer | FK, NN | Assigned role |
| full_name | varchar(100) | NN | User name |
| email | varchar(255) | NN, UQ | Unique login email |
| password_hash | text | NN | Password hash, not plaintext |
| is_active | boolean | NN, default TRUE | Account status |
| failed_login_attempts | integer | NN, default 0, CK >= 0 | Failed login counter |
| locked_until | timestamp | Nullable | Account lock expiry |
| last_login_at | timestamp | Nullable | Last successful login |
| created_at | timestamp | NN, default CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | timestamp | NN, default CURRENT_TIMESTAMP | Update timestamp |

## user_sessions

| Attribute | Type | Constraint | Meaning |
|---|---|---|---|
| session_id | integer | PK, NN | Session identifier |
| user_id | integer | FK, NN, ON DELETE CASCADE | Session owner |
| token_hash | text | NN, UQ | Unique session token hash |
| expires_at | timestamp | NN | Expiry time |
| revoked_at | timestamp | Nullable | Revocation time |
| created_at | timestamp | NN, default CURRENT_TIMESTAMP | Creation time |

## password_reset_tokens

| Attribute | Type | Constraint | Meaning |
|---|---|---|---|
| token_id | integer | PK, NN | Reset-token identifier |
| user_id | integer | FK, NN, ON DELETE CASCADE | Requesting user |
| token_hash | text | NN, UQ | Unique reset-token hash |
| expires_at | timestamp | NN | Expiry time |
| used_at | timestamp | Nullable | Consumption time |
| created_at | timestamp | NN, default CURRENT_TIMESTAMP | Creation time |

## risk_assessment

| Attribute | Type | Constraint | Meaning |
|---|---|---|---|
| risk_assessment_id | integer | PK, NN | Assessment identifier |
| company_id | integer | FK, NN, ON DELETE CASCADE | Assessed company |
| risk_score | numeric(5,2) | NN, CK 0–100 | Risk score |
| risk_level | varchar(20) | NN, CK allowed labels | LOW, MEDIUM, HIGH or CRITICAL |
| assessed_at | timestamp | NN, default CURRENT_TIMESTAMP | Assessment time |
| model_version | varchar(50) | Nullable | Model version |
| explanation | text | Nullable | Assessment explanation |
| assessed_by | integer | Nullable FK, ON DELETE SET NULL | Optional assessing user |

A BEFORE UPDATE OR DELETE trigger protects existing assessments; insert a new assessment to preserve history.

## risk_assessment_audit

| Attribute | Type | Constraint | Meaning |
|---|---|---|---|
| audit_id | integer | PK, NN | Audit row identifier |
| risk_assessment_id | integer | NN; no FK declared | Copied source assessment ID |
| company_id | integer | NN; no FK declared | Copied company ID |
| risk_score | numeric | NN, CK 0–100 | Captured risk score |
| logged_at | timestamp | NN, default now() | Audit timestamp |
| action_type | varchar(20) | NN, CK = INSERT | Audited action |
| risk_level | varchar(20) | NN, CK allowed labels | Captured classification |
| model_version | varchar(50) | Nullable | Captured model version |
| explanation | text | Nullable | Captured explanation |
| assessed_by | integer | Nullable; no FK declared | Copied assessor ID |

The AFTER INSERT trigger on `risk_assessment` creates audit snapshots. The current DDL does not declare foreign keys on this audit relation.

## Additional integrity and implementation notes

- The non-null UNIQUE attributes `roles.role_name`, `users.email`, `user_sessions.token_hash`, and `password_reset_tokens.token_hash` are candidate keys.
- `companies.registration_number` is nullable despite being UNIQUE, so it is not treated as a candidate key.
- `financial_records(company_id, fiscal_year)` is a composite candidate key enforced by UNIQUE.
- The tracked DDL defines an index on `risk_assessment(company_id, assessed_at DESC)`, a `company_risk_view` view, risk-assessment functions/procedure, an audit trigger, and an append-only protection trigger.
- This dictionary reflects tracked PostgreSQL DDL only. Vector embeddings, events, news and evidence-document relations are not included because they are not present in that DDL.
