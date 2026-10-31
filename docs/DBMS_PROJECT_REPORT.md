# AEGIS — AI-Powered Financial Risk & Event Intelligence Platform
## DBMS Project Report

> **Submission evidence note:** This report is prepared from the tracked repository and project details available at the time of writing. Runtime screenshots, live database execution output, application demo evidence, and any unverified features must be added only after they are actually captured. Do not submit placeholders as completed evidence.

## 1. Project Title

**AEGIS — AI-Powered Financial Risk & Event Intelligence Platform**

## 2. Student Details

| Student name | SRN | Responsibility |
|---|---|---|
| Akash Shivanand Bagoji | PES1UG24AM339 | Database design, PostgreSQL implementation, SQL portfolio, database documentation, and data-layer design |
| Dhanraj Rathod | PES1UG24AM359 | Backend/API, frontend, application integration, and deployment responsibility |

The responsibility split is recorded in `docs/TEAM_CONTRIBUTION.md`. Actual completed contributions should be evidenced by commits, pull requests, tests, or demonstrations.

## 3. Abstract

AEGIS is a financial risk intelligence platform designed to organize company information, historical financial records, user access data, and time-based risk assessments in a relational database. The database preserves historical risk results rather than replacing earlier assessments. Database constraints support data integrity, while stored routines, views, and triggers provide reusable operations and audit behavior.

The current repository implementation focuses on PostgreSQL. It contains eight core relations: companies, financial_records, roles, users, user_sessions, password_reset_tokens, risk_assessment, and risk_assessment_audit. A SQL query portfolio demonstrates filtering, sorting, joins, aggregation, subqueries, common table expressions, and window functions. The database design is documented through ER, relational-schema, data-dictionary, functional-dependency, and normalization documents.

The broader project vision includes an API layer, web dashboard, machine-learning risk signals, and evidence retrieval. Those components are design targets and are not represented as completed source code in the current tracked repository unless separately implemented and evidenced.

## 4. Technology Stack

### 4.1 Implemented and tracked

| Technology | Purpose | Status |
|---|---|---|
| PostgreSQL 18.x | Primary relational database | Schema dump tracked |
| PL/pgSQL | Stored functions, procedure, and trigger logic | Included in schema dump |
| pgcrypto | Cryptographic database extension used by schema | Extension declaration included |
| SQL | DDL and analytical query portfolio | Tracked |

### 4.2 Proposed application/integration technologies

| Technology | Intended purpose | Repository evidence |
|---|---|---|
| FastAPI / Python | REST API and service layer | Design only; backend source not present in current tracked tree |
| Next.js / React / TypeScript | User-facing dashboard | Design only; frontend source not present in current tracked tree |
| pgvector | Semantic vector retrieval | Not installed or defined in tracked DDL |
| ML model pipeline | Financial risk signal generation | Design only; no trained model or evaluation results tracked |

## 5. SQL — Database Commands

The authoritative schema is `database/ddl/01_schema.sql`. It defines the database objects. The following command categories are represented in the schema and query portfolio:

1. **DDL:** CREATE TABLE, CREATE SEQUENCE, ALTER TABLE, CREATE INDEX, CREATE VIEW, CREATE FUNCTION, CREATE PROCEDURE, CREATE TRIGGER.
2. **DML examples:** SELECT queries are provided in the query portfolio. Live INSERT/UPDATE/DELETE demonstrations must use a test database and respect append-only risk history.
3. **Constraints:** primary keys, foreign keys, UNIQUE constraints, CHECK constraints, NOT NULL requirements, and default values.
4. **Joins and aggregation:** INNER JOIN, LEFT JOIN, COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING.
5. **Subqueries and CTEs:** scalar and correlated subqueries, IN, EXISTS, NOT EXISTS, and WITH queries.
6. **Window functions:** ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, and running averages.
7. **Programmability:** stored functions, procedure, views, and triggers.

### 5.1 Query files

| File | Topics |
|---|---|
| `database/queries/01_basic_queries.sql` | Basic retrieval, filtering, sorting, NULL handling |
| `database/queries/02_joins_and_aggregations.sql` | Joins, aggregate functions, grouping, HAVING |
| `database/queries/03_subqueries_ctes_window_functions.sql` | Subqueries, CTEs, window functions |

### 5.2 Database verification

The read-only catalog and data verification script is `database/verification/01_schema_verification.sql`. It checks relation presence, columns, constraints, indexes, triggers, views, routines, extensions, and row counts. `database/seeds/01_demo_data.sql` supplies repeatable synthetic demo records. GitHub Actions runs the schema, seed, analytical queries, catalog verification, and behavioral tests against a disposable PostgreSQL 18 service. This is automated execution evidence; it is distinct from screenshots of a local database client.

### 5.3 Historical risk and audit behavior

Risk assessments are intended to be append-only through the modification-prevention trigger in the schema. An AFTER INSERT trigger copies assessment details into `risk_assessment_audit`. The current audit relation does not declare foreign keys for its copied source identifiers; this is documented as a trigger-maintained logical association.

## 6. NoSQL / Vector Database Commands

**Current status:** The core schema does not install pgvector. A separate optional migration and query reference is now tracked at `database/vector/01_pgvector_evidence.sql`. It contains extension creation, an evidence table with a 384-dimensional vector column, an HNSW cosine index, and similarity-search examples. It is intentionally excluded from core CI because pgvector is not installed in the standard PostgreSQL service image. The migration is not claimed as executed; a compatible embedding model and pgvector-enabled server are prerequisites.

The optional migration contains commands of the following form:

```sql
-- Illustrative future commands only; requires pgvector installation.
CREATE EXTENSION IF NOT EXISTS vector;

-- Example table; choose embedding dimension to match the selected model.
CREATE TABLE evidence_embeddings (
    evidence_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_uri TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Example approximate-nearest-neighbour index.
CREATE INDEX evidence_embeddings_cosine_idx
ON evidence_embeddings
USING hnsw (embedding vector_cosine_ops);

-- Example similarity search; replace the vector with a real model output.
-- SELECT evidence_id, source_uri, content
-- FROM evidence_embeddings
-- ORDER BY embedding <=> '[...]'::vector
-- LIMIT 5;
```

Do not present these illustrative commands as completed work. A real implementation must specify the embedding model, dimension, source provenance, update strategy, index choice, and retrieval evaluation.

## 7. Next.js — Project Tree Structure

The current tracked repository does not contain a Next.js application. The following is a proposed target structure, not the present repository tree:

```text
frontend/
├── app/
│   ├── login/
│   ├── dashboard/
│   ├── companies/
│   └── risk-assessments/
├── components/
├── lib/
├── services/
├── types/
└── package.json
```

The actual repository tree currently contains the PostgreSQL DDL, SQL query files, README, and documentation under `docs/`. See the root README for the verified file inventory.

## 8. Sample Screenshots of Application Code and Demo

**Evidence to attach before submission:**

1. PostgreSQL schema/tables visible in the database client.
2. ER diagram.
3. Successful execution of representative JOIN and aggregate queries.
4. Successful execution of CTE and window-function queries.
5. Trigger/audit behavior demonstrated in a test database.
6. Application login/dashboard screenshots, only if the application is implemented.
7. End-to-end demo screenshots, only if the complete workflow is running.

No local database-client or end-to-end application screenshot is embedded because no such image was available from the connected repository. The automated PostgreSQL 18 CI run is linked from the README and provides reproducible execution evidence, including transaction behavior, structural assertions, row-level locking, SELECT FOR UPDATE, and REPEATABLE READ behavior using two independent sessions. A local-client screenshot or application demo image must not be fabricated; the web application is not implemented in the tracked repository.

## 9. Evaluation Rubric — Completion Status

| Evaluation area | Current evidence | Status |
|---|---|---|
| Project title, scope, abstract | This report and project requirements | Documented |
| Relational schema and ER model | DDL, ER design, relational schema, data dictionary | Documented in repository |
| Keys and constraints | PostgreSQL schema dump | Implemented in tracked DDL; runtime verification pending |
| Functional dependencies | Functional-dependency document | Documented |
| Normalization | Normalization document | Documented analysis |
| SQL query coverage | Three SQL query files; synthetic seed dataset; PostgreSQL 18 CI | Implemented and executed in CI |
| Views, functions, procedure, triggers | Schema dump; behavioral tests; PostgreSQL 18 CI | Implemented and behavior-tested in CI |
| Transactions | `database/verification/03_transaction_demo.sql`; PostgreSQL 18 CI | COMMIT, SAVEPOINT rollback, and full ROLLBACK are executed and asserted in CI |
| Concurrency and isolation | `database/verification/05_concurrency_demo.sh`; PostgreSQL 18 CI | Two-session row-lock waiting, SELECT FOR UPDATE, and REPEATABLE READ snapshot behavior are asserted in CI |
| Final structural audit | `database/verification/04_final_structure_assertions.sql`; PostgreSQL 18 CI | Required tables, integrity constraints, triggers, view, routines, and index are asserted in CI |
| NoSQL/vector database | Optional pgvector migration and similarity-query reference | Documented; requires pgvector-enabled runtime and real embedding model |
| FastAPI backend | API design document only | Not implemented in tracked source |
| Next.js frontend | Proposed project tree only | Not implemented in tracked source |
| ML model and evaluation | ML design document only | Not implemented in tracked source |
| Local database-client screenshots / web application demo | No authentic local-client or application screenshots available; CI logs linked | Local screenshots pending; no web application in tracked source |
| GitHub source and documentation | Repository and merged PRs | Available |

## 10. Conclusion

The current AEGIS repository provides a PostgreSQL-centered DBMS foundation with a normalized relational design, integrity constraints, historical risk assessment storage, audit-trigger logic, and a structured SQL query portfolio. Its documentation now includes the ER model, relational schema, data dictionary, functional dependencies, normalization analysis, system architecture, API design, and ML design.

The relational DBMS implementation is now automatically exercised in PostgreSQL 18 CI using a repeatable synthetic dataset, catalog checks, analytical SQL, and behavioral integration tests. The optional pgvector migration is documented but not executed. A complete end-to-end AI application still requires the API, frontend, production vector retrieval, ML pipeline, and authentic application demo evidence; these are not claimed as completed.

## Appendix A — Repository links

- Repository: https://github.com/akashsb2005/aegis-financial-risk-intelligence
- Database schema: `database/ddl/01_schema.sql`
- SQL query portfolio: `database/queries/`
- Database design: `docs/database/`
- API design: `docs/api/API_DESIGN.md`
- ML design: `docs/ml/ML_DESIGN.md`
- Team contributions: `docs/TEAM_CONTRIBUTION.md`
