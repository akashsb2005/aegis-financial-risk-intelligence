# AEGIS Attribute Closure and Candidate-Key Analysis

## 1. Purpose and scope

This document shows attribute-closure calculations for the relations in the current PostgreSQL DDL. It supports the candidate-key and normalization discussion in `FUNCTIONAL_DEPENDENCIES.md` and `NORMALIZATION.md`.

Notation: for an attribute set X, X+ is the set of all attributes functionally determined by X under the stated functional-dependency (FD) set.

The calculations below use the key-based dependencies justified by the primary keys and non-null UNIQUE constraints in `database/ddl/01_schema.sql`. For `financial_records`, the additional business key `(company_id, fiscal_year)` is included because the DDL enforces it as UNIQUE and both attributes are NOT NULL.

A nullable UNIQUE column such as `companies.registration_number` is not treated as a candidate key.

## 2. Closure calculation method

To calculate X+:

1. Start with X+ = X.
2. Find every FD A -> B whose determinant A is contained in the current X+.
3. Add B to X+.
4. Repeat until no attribute can be added.
5. If X+ contains every attribute of the relation, X is a superkey. If no proper subset of X is a superkey, X is a candidate key.

## 3. Relation-wise candidate keys and closures

### 3.1 COMPANIES

Attributes: `company_id, company_name, registration_number, industry, country, annual_revenue, employee_count, created_at, updated_at`.

FD: `company_id -> all remaining attributes`.

Calculation:

- Start: `{company_id}+` = `{company_id}`.
- Apply the FD: add `company_name, registration_number, industry, country, annual_revenue, employee_count, created_at, updated_at`.
- Result: `{company_id}+` contains every COMPANIES attribute.

Candidate key: `{company_id}`.

### 3.2 FINANCIAL_RECORDS

Attributes: `financial_record_id, company_id, fiscal_year, revenue, net_profit, total_assets, total_liabilities, total_debt, shareholders_equity, operating_cash_flow, created_at`.

FDs:

- `financial_record_id -> all remaining attributes`.
- `(company_id, fiscal_year) -> financial_record_id, revenue, net_profit, total_assets, total_liabilities, total_debt, shareholders_equity, operating_cash_flow, created_at`.

Closure of the primary key:

- Start: `{financial_record_id}+` = `{financial_record_id}`.
- Apply the first FD to add all remaining attributes.
- Result: the closure is the complete FINANCIAL_RECORDS attribute set.

Closure of the composite UNIQUE key:

- Start: `{company_id, fiscal_year}+` = `{company_id, fiscal_year}`.
- Apply the second FD to add `financial_record_id` and all financial measures and `created_at`.
- Result: the closure is the complete FINANCIAL_RECORDS attribute set.

Minimality:

- `{company_id}+` does not determine `fiscal_year` or the financial record.
- `{fiscal_year}+` does not determine `company_id` or the financial record.
- Therefore neither proper subset is a superkey.

Candidate keys: `{financial_record_id}` and `{company_id, fiscal_year}`.

### 3.3 ROLES

Attributes: `role_id, role_name, description, created_at`.

FDs: `role_id -> role_name, description, created_at`; `role_name -> role_id, description, created_at`.

Both `{role_id}+` and `{role_name}+` contain every ROLES attribute.

Candidate keys: `{role_id}` and `{role_name}`.

### 3.4 USERS

Attributes: `user_id, role_id, full_name, email, password_hash, is_active, failed_login_attempts, locked_until, last_login_at, created_at, updated_at`.

FDs: `user_id -> all remaining attributes`; `email -> user_id, role_id, full_name, password_hash, is_active, failed_login_attempts, locked_until, last_login_at, created_at, updated_at`.

Both `{user_id}+` and `{email}+` contain every USERS attribute.

Candidate keys: `{user_id}` and `{email}`.

### 3.5 USER_SESSIONS

Attributes: `session_id, user_id, token_hash, expires_at, revoked_at, created_at`.

FDs: `session_id -> user_id, token_hash, expires_at, revoked_at, created_at`; `token_hash -> session_id, user_id, expires_at, revoked_at, created_at`.

Both closures contain every USER_SESSIONS attribute.

Candidate keys: `{session_id}` and `{token_hash}`.

### 3.6 PASSWORD_RESET_TOKENS

Attributes: `token_id, user_id, token_hash, expires_at, used_at, created_at`.

FDs: `token_id -> user_id, token_hash, expires_at, used_at, created_at`; `token_hash -> token_id, user_id, expires_at, used_at, created_at`.

Both closures contain every PASSWORD_RESET_TOKENS attribute.

Candidate keys: `{token_id}` and `{token_hash}`.

### 3.7 RISK_ASSESSMENT

Attributes: `risk_assessment_id, company_id, risk_score, risk_level, assessed_at, model_version, explanation, assessed_by`.

FD: `risk_assessment_id -> all remaining attributes`.

The closure of `{risk_assessment_id}` contains every RISK_ASSESSMENT attribute.

Candidate key: `{risk_assessment_id}`.

A company may have multiple assessments, so `company_id` alone does not determine an assessment's score, level, time, or model version.

### 3.8 RISK_ASSESSMENT_AUDIT

Attributes: `audit_id, risk_assessment_id, company_id, risk_score, logged_at, action_type, risk_level, model_version, explanation, assessed_by`.

FD: `audit_id -> all remaining attributes`.

The closure of `{audit_id}` contains every RISK_ASSESSMENT_AUDIT attribute.

Candidate key: `{audit_id}`.

## 4. Candidate-key summary

| Relation | Candidate key(s) supported by the current DDL |
|---|---|
| companies | `company_id` |
| financial_records | `financial_record_id`; `(company_id, fiscal_year)` |
| roles | `role_id`; `role_name` |
| users | `user_id`; `email` |
| user_sessions | `session_id`; `token_hash` |
| password_reset_tokens | `token_id`; `token_hash` |
| risk_assessment | `risk_assessment_id` |
| risk_assessment_audit | `audit_id` |

## 5. Lossless decomposition and dependency preservation

No relation decomposition is proposed by the current normalization analysis. The existing relations are retained as designed, so there is no newly decomposed relation set for which a non-trivial lossless-join or dependency-preservation proof is being claimed.

If a future design change decomposes a relation R into R1, R2, ...:

- Losslessness must be demonstrated (for a binary decomposition, a standard sufficient test is that the common attributes functionally determine all attributes of at least one component under the projected FD set).
- Dependency preservation must be checked by projecting the original FDs onto the decomposed relations and confirming that their union implies the original dependencies.
- The proposed decomposition must also be checked against foreign keys, application queries, and historical-data requirements.

Do not state that a decomposition is lossless or dependency-preserving merely because the current schema has multiple tables. Those properties apply to a specific decomposition of a relation.

## 6. Limitations

These closures are based on the dependencies established by the tracked DDL and documented business rule for one financial record per company/fiscal year. They do not assert undocumented business dependencies. If new business rules are introduced, update the FD set and recalculate closures before changing the normalization conclusion.
