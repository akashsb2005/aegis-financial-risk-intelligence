# AEGIS Database Design

## 1. Database Technology

AEGIS uses PostgreSQL as its primary relational database management system.

PostgreSQL was selected because the project requires strong relational integrity, advanced SQL capabilities, transactions, indexing, analytical queries, stored functions and procedures, triggers, and support for vector similarity search through pgvector.

The database is named `aegis_db` and is accessed using the dedicated `aegis_user` database account.

---

## 2. Database Design Goals

The database is designed to provide:

- Strong entity and referential integrity
- Normalized relational data storage
- Historical preservation of risk assessments
- Database-level validation of important business rules
- Support for analytical SQL queries
- Efficient retrieval of company risk history
- Auditability of risk assessment creation
- A foundation for ML-generated risk signals
- Integration with the FastAPI backend and Next.js frontend

The database is treated as a core part of the AEGIS decision-support system rather than only as application storage.

---

## 3. Core Entities

The current relational design includes entities for:

- Companies
- Users
- Roles
- User sessions
- Password reset tokens
- Financial records
- Risk assessments
- Risk assessment audit history

The `companies` table represents financial entities being analyzed.

The `financial_records` table stores historical financial information associated with companies.

The `risk_assessment` table stores risk assessments generated for companies at specific points in time.

The `risk_assessment_audit` table stores historical snapshots of risk assessment creation events.

---

## 4. Risk Assessment Design

The `risk_assessment` table contains:

- `risk_assessment_id` - primary key
- `company_id` - foreign key to `companies`
- `risk_score` - numeric score from 0 to 100
- `risk_level` - LOW, MEDIUM, HIGH, or CRITICAL
- `assessed_at` - assessment timestamp
- `model_version` - version of the model that produced the assessment
- `explanation` - explanation associated with the assessment
- `assessed_by` - optional reference to the user responsible for the assessment

The database enforces the valid risk score range and valid risk levels using CHECK constraints.

---

## 5. Historical Risk Assessment Strategy

AEGIS uses an append-oriented design for risk assessments.

An existing risk assessment is not silently modified when a new assessment becomes available.

Instead, a new risk assessment record is inserted with its own timestamp and model version.

For example:

```text
Assessment 1 -> 80.00 HIGH
Assessment 2 -> 35.25 MEDIUM
Assessment 3 -> 65.50 HIGH
Assessment 4 -> 74.25 HIGH
Assessment 5 -> 81.50 CRITICAL
Assessment 6 -> 81.50 CRITICAL

---

## 6. Risk Assessment Audit History

The `risk_assessment_audit` table records immutable snapshots when risk assessments are created.

The audit table contains:

- `audit_id` - primary key
- `risk_assessment_id` - identifier of the source assessment
- `company_id` - identifier of the assessed company
- `risk_score` - captured risk score
- `logged_at` - timestamp of the audit event
- `action_type` - currently restricted to `INSERT`
- `risk_level` - captured risk level; NOT NULL
- `model_version` - captured model version
- `explanation` - captured assessment explanation
- `assessed_by` - captured user reference

The audit table requires `risk_level` to be NOT NULL because every audit snapshot must contain a valid risk classification.

The audit records preserve the state of the assessment at creation time rather than relying on the current contents of the `risk_assessment` table.

---

## 7. Audit Trigger

An `AFTER INSERT` trigger on `risk_assessment` automatically creates a corresponding record in `risk_assessment_audit`.

This ensures that audit logging occurs at the database level whenever a new risk assessment is inserted.

The trigger records:

- Risk assessment identifier
- Company identifier
- Risk score
- Risk level
- Model version
- Explanation
- Assessed-by user
- Insert action
- Audit timestamp

This design prevents the application from being solely responsible for creating audit records.

---

## 8. Append-Only Protection Trigger

AEGIS prevents modification or deletion of existing risk assessments.

A `BEFORE UPDATE OR DELETE` trigger raises a database exception when an existing risk assessment is modified or deleted.

The intended operation is:

```text
New assessment available
        |
        v
INSERT new risk_assessment row
        |
        v
AFTER INSERT trigger
        |
        v
Create audit snapshot