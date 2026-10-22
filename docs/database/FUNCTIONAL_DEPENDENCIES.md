# AEGIS Functional Dependencies

## 1. Purpose

This document identifies the functional dependencies present in the AEGIS relational database design.

Functional dependencies are used to reason about candidate keys, normalization, redundancy, and relational integrity.

The dependencies documented here are derived from the implemented PostgreSQL schema.

---

## 2. Functional Dependency Definition

A functional dependency describes a relationship between attributes.

For a functional dependency:

`A -> B`

attribute A determines attribute B.

This means that for a given value of A, there can be only one corresponding value of B within the relation.

---

## 3. Functional Dependencies by Relation

### 3.1 Companies

Primary key:

`company_id`

Functional dependency:

`company_id -> company_name, registration_number, industry, country, annual_revenue, employee_count, created_at, updated_at`

The company identifier uniquely identifies a company record.

---

### 3.2 Financial Records

Primary key:

`financial_record_id`

Functional dependency:

`financial_record_id -> company_id, fiscal_year, revenue, net_profit, total_assets, total_liabilities, total_debt, shareholders_equity, operating_cash_flow, created_at`

The database also enforces uniqueness on:

`(company_id, fiscal_year)`

Therefore, within the implemented design:

`(company_id, fiscal_year) -> revenue, net_profit, total_assets, total_liabilities, total_debt, shareholders_equity, operating_cash_flow`

This prevents multiple financial records for the same company and fiscal year.

---

### 3.3 Roles

Primary key:

`role_id`

Functional dependency:

`role_id -> role_name, description, created_at`

The role identifier uniquely identifies a role.

---

### 3.4 Users

Primary key:

`user_id`

Functional dependency:

`user_id -> role_id, full_name, email, password_hash, is_active, failed_login_attempts, locked_until, last_login_at, created_at, updated_at`

The database also enforces uniqueness on `email`.

---

### 3.5 User Sessions

Primary key:

`session_id`

Functional dependency:

`session_id -> user_id, token_hash, expires_at, revoked_at, created_at`

The database also enforces uniqueness on `token_hash`.

---

### 3.6 Password Reset Tokens

Primary key:

`token_id`

Functional dependency:

`token_id -> user_id, token_hash, expires_at, used_at, created_at`

The database also enforces uniqueness on `token_hash`.

---

### 3.7 Risk Assessments

Primary key:

`risk_assessment_id`

Functional dependency:

`risk_assessment_id -> company_id, risk_score, risk_level, assessed_at, model_version, explanation, assessed_by`

A company can have multiple risk assessments over time.

Therefore:

`company_id -> risk_score`

is not a valid functional dependency in the AEGIS design.

The assessment identifier is required to uniquely identify an individual historical assessment.

---

### 3.8 Risk Assessment Audit

Primary key:

`audit_id`

Functional dependency:

`audit_id -> risk_assessment_id, company_id, risk_score, logged_at, action_type, risk_level, model_version, explanation, assessed_by`

The audit identifier uniquely identifies an audit snapshot.

---

## 4. Important Non-Dependencies

The following dependencies should not be assumed:

`company_id -> risk_score`

A company may have multiple risk assessments.

`company_id -> risk_level`

Risk classification may change between assessments.

`company_id -> model_version`

Different model versions may generate assessments for the same company.

`fiscal_year -> financial data`

Different companies can have financial records for the same fiscal year.

These non-dependencies are important because AEGIS preserves historical financial and risk information rather than treating a company as having only one current risk state.

---

## 5. Candidate Keys

A candidate key is a minimal set of attributes that uniquely identifies each tuple in a relation.

The primary keys in the implemented schema are candidate keys:

- `companies.company_id`
- `financial_records.financial_record_id`
- `roles.role_id`
- `users.user_id`
- `user_sessions.session_id`
- `password_reset_tokens.token_id`
- `risk_assessment.risk_assessment_id`
- `risk_assessment_audit.audit_id`

The following additional unique constraints also provide candidate keys because their attributes are required and unique:

- `roles.role_name`
- `users.email`
- `user_sessions.token_hash`
- `password_reset_tokens.token_hash`
- `(financial_records.company_id, financial_records.fiscal_year)`

`companies.registration_number` is enforced as UNIQUE but is nullable in the implemented schema. Therefore, it is treated as a unique attribute rather than being listed as a candidate key.

The candidate key `(company_id, fiscal_year)` for `financial_records` is particularly important because it represents the business rule that a company has at most one financial record for a given fiscal year.

---

## 6. Historical Data Considerations

AEGIS is designed to preserve historical financial and risk information.

A company is therefore not treated as having a single immutable risk score.

Instead, multiple risk assessments may exist for the same company at different points in time.

The functional dependency:

`risk_assessment_id -> risk_score, risk_level, assessed_at, model_version`

allows each assessment to retain its own historical state.

This supports temporal analysis, model-version comparison, and risk trend analysis.

---

## 7. Relationship Between Functional Dependencies and Normalization

Functional dependencies provide the basis for evaluating normalization.

The AEGIS schema separates company information, financial records, user information, roles, risk assessments, sessions, reset tokens, and audit history into separate relations.

This separation reduces unnecessary repetition and helps avoid update, insertion, and deletion anomalies.

Normalization analysis is documented separately in `NORMALIZATION.md`.

---

## 8. Summary

The AEGIS relational design uses primary keys and enforced unique constraints to establish stable determinants for relation attributes.

Functional dependencies demonstrate why entities are separated into independent relations and why historical risk assessments are represented as separate records.

This design supports data integrity, historical preservation, analytical queries, and integration with the ML and application layers.