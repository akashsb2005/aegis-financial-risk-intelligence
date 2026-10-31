# AEGIS — Financial Risk & Event Intelligence Platform

AEGIS is a database-centric financial risk intelligence project. Its current, tracked implementation is built around PostgreSQL and models companies, financial records, users and roles, sessions, password-reset tokens, risk assessments, and audit snapshots.

> **Implementation-status note:** The repository currently contains the PostgreSQL schema, SQL query portfolio, and database design documentation. A FastAPI service, Next.js application, pgvector deployment, live news/event ingestion, and a trained ML model are not included in the tracked source tree at this stage. They are documented as proposed integration layers, not as completed features.

## Repository contents

| Path | Purpose |
|---|---|
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
| `docs/database/FUNCTIONAL_DEPENDENCIES.md` | Functional-dependency analysis |
| `docs/database/NORMALIZATION.md` | 1NF, 2NF, 3NF, and BCNF assessment |
| `docs/database/SYSTEM_ARCHITECTURE.md` | Current implementation boundary and proposed architecture |
| `docs/api/API_DESIGN.md` | Proposed API contract and integration boundary |
| `docs/ml/ML_DESIGN.md` | Proposed ML workflow and validation requirements |
| `docs/TEAM_CONTRIBUTION.md` | Team roles and contribution record |

## Database setup

The schema targets PostgreSQL 18.x and enables the `pgcrypto` extension. Create a database, connect to it, and apply `database/ddl/01_schema.sql` using a PostgreSQL client that supports the commands emitted by `pg_dump`.

The dump contains database objects, not a portable guarantee of application users, passwords, or production secrets. Configure database roles and credentials separately for each environment. Never commit real credentials.

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

## Team

See [Team Contributions](docs/TEAM_CONTRIBUTION.md) for the student details and responsibility split.
