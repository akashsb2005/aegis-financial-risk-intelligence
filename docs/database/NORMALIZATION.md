

## 1. Purpose

This document evaluates the normalization of the AEGIS PostgreSQL relational schema. The analysis uses the implemented DDL and the functional dependencies documented in `FUNCTIONAL_DEPENDENCIES.md`.

The objectives are to evaluate First Normal Form (1NF), Second Normal Form (2NF), Third Normal Form (3NF), and Boyce–Codd Normal Form (BCNF), while avoiding unnecessary changes to a working schema.

## 2. Scope and Method

The analysis covers these relations:

- `companies`
- `financial_records`
- `roles`
- `users`
- `user_sessions`
- `password_reset_tokens`
- `risk_assessment`
- `risk_assessment_audit`

Primary keys and enforced UNIQUE constraints are used to identify guaranteed key-based functional dependencies. Additional business dependencies are considered only when supported by the project requirements or documented domain rules.

The analysis is based on the current DDL. It does not claim to prove business rules that are not represented in the schema or project documentation.

## 3. Candidate Keys and Prime Attributes

A candidate key is a minimal set of attributes that uniquely identifies a tuple. An attribute that belongs to at least one candidate key is a prime attribute.

The implemented primary keys are:

| Relation | Primary key |
|---|---|
| companies | company_id |
| financial_records | financial_record_id |
| roles | role_id |
| users | user_id |
| user_sessions | session_id |
| password_reset_tokens | token_id |
| risk_assessment | risk_assessment_id |
| risk_assessment_audit | audit_id |

Additional candidate keys established by non-null UNIQUE constraints are:

- `financial_records`: `(company_id, fiscal_year)`
- `roles`: `role_name`
- `users`: `email`
- `user_sessions`: `token_hash`
- `password_reset_tokens`: `token_hash`

`companies.registration_number` is nullable. Although it has a UNIQUE constraint, it is not treated here as a candidate key because candidate-key attributes must identify every tuple and be non-null.

The current DDL does not establish any additional candidate keys for `risk_assessment` or `risk_assessment_audit`.

## 4. First Normal Form (1NF)

A relation satisfies 1NF when its attributes contain atomic values and it has no repeating groups.

The current schema uses scalar types such as integer, varchar, numeric, timestamp, boolean, and text. It does not declare array-valued columns or repeating groups.

On this structural evidence, the relations are consistent with 1NF. This conclusion assumes that text fields such as `explanation` and `description` store single logical values rather than multiple independent values encoded into a string.

## 5. Second Normal Form (2NF)

A relation is in 2NF when it is in 1NF and no non-prime attribute is partially dependent on a proper subset of a candidate key.

Most AEGIS relations have single-attribute primary keys. A partial dependency on a proper subset of a single-attribute key is not possible.

The important composite candidate key is:

`financial_records(company_id, fiscal_year)`

The business rule represented by the UNIQUE constraint is that a company has at most one financial record for a given fiscal year.

The documented financial attributes, including revenue, net profit, assets, liabilities, debt, shareholders' equity, operating cash flow, and record creation time, are identified by the complete candidate key under the implemented uniqueness rule.

The documented dependencies do not establish that a non-prime financial attribute depends on `company_id` alone or `fiscal_year` alone. Therefore, no partial dependency violating 2NF has been identified.

This conclusion should be revisited if future requirements introduce attributes that describe a company independently of fiscal year. Such attributes would normally belong in `companies`, not in `financial_records`.

## 6. Third Normal Form (3NF)

A relation satisfies 3NF if, for every non-trivial functional dependency X -> A, either X is a superkey or A is a prime attribute.

The documented dependencies are principally key-based: each relation's primary key determines its other attributes. The additional non-null UNIQUE keys listed above also act as candidate keys for their respective relations.

The current dependency documentation does not identify a transitive dependency that requires decomposition to satisfy 3NF.

The separation of roles from users is an important example. User records store `role_id`, while role names and descriptions are stored in `roles`. This avoids repeating role descriptions for every user.

Similarly, company details are stored in `companies`, while fiscal-year financial values are stored in `financial_records`.

Based on the documented dependencies, no additional decomposition is currently justified for 3NF. This is a conclusion about the known dependencies, not a guarantee against every possible undocumented business dependency.

## 7. Boyce–Codd Normal Form (BCNF)

A relation is in BCNF when the determinant of every non-trivial functional dependency is a superkey.

The documented key-based dependencies have candidate keys as their determinants. No additional non-key determinant has been established by the current dependency analysis.

Therefore, the current relations appear to satisfy BCNF with respect to the documented dependencies. A stronger conclusion would require validating all relevant business dependencies, not only those implied by primary keys and UNIQUE constraints.

## 8. Relation-by-Relation Summary

| Relation | Normalization assessment |
|---|---|
| companies | Consistent with 1NF; key-based dependencies show no identified 2NF, 3NF, or BCNF violation. |
| financial_records | Composite candidate key is `(company_id, fiscal_year)`; no partial dependency has been identified. |
| roles | Role attributes are determined by the primary key; `role_name` is an additional candidate key. |
| users | User attributes are determined by the primary key; `email` is an additional candidate key. |
| user_sessions | Session attributes are determined by the primary key; `token_hash` is an additional candidate key. |
| password_reset_tokens | Token attributes are determined by the primary key; `token_hash` is an additional candidate key. |
| risk_assessment | Each assessment has its own key and may represent a different point in time. |
| risk_assessment_audit | Each audit snapshot has its own key and preserves a recorded assessment state. |

## 9. Historical Risk Data

AEGIS preserves risk assessments as separate records rather than assuming that each company has one permanent risk score.

The `risk_assessment` relation contains assessment-specific information, including the company, risk score, risk level, assessment time, model version, explanation, and assessor.

The `risk_assessment_audit` relation records snapshots created by the audit trigger. Its `audit_id` identifies an audit row.

The append-only protection trigger on `risk_assessment` prevents updates and deletes through the ordinary table operations covered by that trigger. New assessments are inserted instead of silently overwriting previous assessment states.

These historical design choices support temporal analysis and comparison between assessments and model versions. They are preservation and integrity decisions in addition to normalization decisions.

## 10. Lossless Decomposition and Dependency Preservation

No additional decomposition is proposed by this analysis because no violation requiring decomposition has been identified in the documented dependencies.

Consequently, the current schema has not been subjected to a new decomposition that requires a separate lossless-join proof.

If a future dependency reveals a normalization violation, the proposed decomposition must be evaluated for:

- Lossless reconstruction of the original relation.
- Preservation of relevant functional dependencies.
- Compatibility with primary keys, foreign keys, application queries, and historical-data requirements.

## 11. Final Conclusion

The implemented AEGIS schema is consistent with 1NF, and the documented functional dependencies do not currently demonstrate a violation of 2NF, 3NF, or BCNF.

The design separates company master data, financial records, identity and access data, risk assessments, and audit snapshots. These separations reduce unnecessary repetition and support integrity and historical analysis.

No schema decomposition is recommended solely for demonstration purposes. The schema should be changed only if a validated requirement or functional dependency reveals a genuine design issue.

## 12. Verification and Limitations

This document is an analysis of the tracked PostgreSQL DDL and the documented functional dependencies. It does not constitute an exhaustive proof of all domain-level dependencies.

Before final submission, verify the conclusions against the current schema, project requirements, and any new business rules introduced during implementation.
