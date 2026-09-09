# AEGIS — Financial Risk & Event Intelligence Platform

## 1. Project Overview

AEGIS is a financial risk and event intelligence platform designed to combine structured financial and market data, financial events, machine-learning-based risk signals, semantic evidence retrieval, and grounded AI explanations within a single system.

The platform is designed primarily as a database-centric system. PostgreSQL acts as the structured source of truth, while vector search is used for semantic retrieval of relevant evidence. Machine-learning components generate analytical signals that are stored and associated with the underlying financial entities and observations.

The system is intended to demonstrate the integration of Database Management Systems, Data Engineering, Machine Learning, Artificial Intelligence, Information Retrieval, Backend Development, and Frontend Development.

---

## 2. Problem Statement

Financial information is distributed across multiple types of data sources including market observations, financial metrics, company events, and textual information such as news.

A user who wants to understand the risk associated with a company or financial security may need to examine several sources and manually correlate changes in market behaviour, financial information, events, and relevant textual evidence.

AEGIS aims to provide a unified system that organizes these heterogeneous data sources, detects potentially significant patterns using machine learning, retrieves relevant evidence, and provides an evidence-grounded explanation of the resulting risk signals.

The system is not intended to provide guaranteed financial advice or autonomous investment decisions.

---

## 3. Motivation

The project combines database engineering with AI/ML rather than treating the database as a simple storage layer.

The motivation is to build a system in which:

- structured financial information is stored consistently;
- relationships between financial entities are explicitly modeled;
- historical market observations can be queried efficiently;
- financial events and textual evidence can be associated with relevant entities;
- machine-learning outputs can be stored and traced;
- semantic retrieval can identify relevant evidence;
- AI explanations can be grounded in retrieved evidence.

---

## 4. Objectives

### 4.1 Primary Objectives

1. Design a robust relational database for financial risk intelligence.
2. Model financial entities and their relationships using an ER model.
3. Convert the ER model into a normalized relational schema.
4. Implement the schema using PostgreSQL.
5. Demonstrate DDL, DML, joins, aggregation, subqueries and advanced SQL.
6. Implement appropriate integrity constraints and indexing.
7. Store and manage financial market, event, risk and analytical data.
8. Develop machine-learning components for financial risk/anomaly analysis.
9. Store ML outputs in the database.
10. Support semantic retrieval using vector representations.
11. Provide evidence-grounded AI explanations.
12. Integrate the database with backend and frontend applications.
13. Provide authentication and role-based access where required.
14. Maintain the complete project using Git and GitHub.

---

## 5. Scope

### 5.1 In Scope

The system will include:

- financial/company entity management;
- securities and related financial instruments;
- market observations;
- financial metrics;
- financial events;
- news or textual evidence;
- risk assessments;
- machine-learning predictions/signals;
- evidence retrieval;
- semantic/vector search;
- grounded AI explanations;
- user access and authentication;
- dashboard-based visualization;
- database-backed APIs;
- database analytics and reporting.

### 5.2 Out of Scope

The following are outside the intended scope:

- guaranteed investment advice;
- autonomous trading;
- execution of financial transactions;
- guaranteed prediction of future market prices;
- replacing licensed financial professionals;
- unrestricted autonomous decision-making by an AI system.

---

## 6. Target Users

Potential users include:

- financial analysts;
- students and researchers;
- risk-analysis users;
- users interested in company and market intelligence;
- administrators responsible for managing the platform.

---

## 7. Functional Requirements

### FR-01 — Company Management

The system shall maintain information about companies or organizations relevant to financial analysis.

### FR-02 — Security Management

The system shall maintain financial securities associated with relevant companies.

### FR-03 — Market Data Management

The system shall store historical market observations such as price and volume information.

### FR-04 — Financial Metrics

The system shall maintain relevant financial metrics associated with financial entities.

### FR-05 — Event Management

The system shall store significant financial or company-related events.

### FR-06 — Evidence Management

The system shall maintain textual evidence such as relevant news or documents.

### FR-07 — Risk Assessment

The system shall store risk assessments associated with financial entities and relevant time periods.

### FR-08 — Machine Learning Signals

The system shall store machine-learning-generated analytical outputs such as anomaly or risk signals.

### FR-09 — Evidence Retrieval

The system shall retrieve relevant evidence associated with a financial entity or analytical query.

### FR-10 — Semantic Search

The system shall support semantic similarity retrieval over supported textual evidence.

### FR-11 — Grounded Explanation

The system shall generate explanations using retrieved structured and textual evidence rather than relying solely on unrestricted model generation.

### FR-12 — Dashboard

The system shall provide a user interface for viewing relevant financial information, risk signals, events and evidence.

### FR-13 — Authentication

The system shall support authenticated access for protected functionality.

### FR-14 — Role-Based Access

Where required, the system shall distinguish between different categories of users and their permitted operations.

### FR-15 — Data Validation

The system shall validate incoming data and maintain database integrity through appropriate constraints.

---

## 8. Non-Functional Requirements

### NFR-01 — Reliability

The system should maintain consistent relationships between financial entities and their associated data.

### NFR-02 — Performance

Frequently accessed financial and analytical information should be retrievable efficiently using appropriate indexes and query design.

### NFR-03 — Security

The system should protect authenticated functionality and prevent unauthorized access to protected operations.

### NFR-04 — Maintainability

The system should use modular architecture and clear separation between database, backend, ML and frontend components.

### NFR-05 — Scalability

The architecture should allow additional financial entities, observations, events, evidence and analytical models to be incorporated without redesigning the entire system.

### NFR-06 — Explainability

AI-generated explanations should be associated with supporting evidence wherever applicable.

### NFR-07 — Reproducibility

The project should maintain source code, database scripts, documentation and development history through Git/GitHub.

---

## 9. Business Rules

The following business rules will guide the database design.

### BR-01

A company may be associated with one or more financial securities.

### BR-02

A security may have many historical market observations.

### BR-03

A company may have multiple financial metrics recorded over different periods.

### BR-04

A company or relevant financial entity may have multiple associated events.

### BR-05

Textual evidence may be associated with one or more relevant financial entities according to the final data model.

### BR-06

Risk assessments must be associated with the financial entity and relevant assessment period.

### BR-07

Machine-learning predictions or signals must be associated with the entity and the model/version that produced them.

### BR-08

Analytical outputs should preserve their timestamp and relevant input context where required.

### BR-09

Historical records should not be silently overwritten when the system requires temporal analysis.

### BR-10

AI explanations should be generated using available evidence retrieved from the system.

---

## 10. Data Requirements

The system is expected to manage several categories of data:

### 10.1 Master Data

- companies;
- securities;
- exchanges or related reference entities;
- users.

### 10.2 Market Data

- historical prices;
- trading volume;
- timestamps;
- derived market indicators.

### 10.3 Financial Data

- financial metrics;
- reporting periods;
- relevant financial indicators.

### 10.4 Event Data

- company events;
- financial events;
- event timestamps;
- event descriptions.

### 10.5 Textual Evidence

- news/articles;
- source metadata;
- publication timestamps;
- textual content;
- semantic representations where applicable.

### 10.6 Analytical Data

- risk assessments;
- anomaly signals;
- ML predictions;
- model metadata;
- prediction timestamps.

### 10.7 System Data

- users;
- roles;
- authentication-related information;
- alerts where required.

---

## 11. Database Requirements

The primary relational database shall be PostgreSQL.

The database design shall support:

- primary keys;
- foreign keys;
- candidate keys where appropriate;
- unique constraints;
- NOT NULL constraints;
- CHECK constraints;
- referential integrity;
- normalized relations;
- indexes;
- transactions;
- views;
- functions/procedures where appropriate;
- triggers where appropriate;
- analytical queries;
- query optimization.

The project shall demonstrate both basic and advanced database operations.

---

## 12. Vector Data Requirements

The system may use PostgreSQL with pgvector for semantic retrieval of textual evidence.

Vector representations will be associated with supported textual records and used to identify semantically relevant evidence for analytical queries.

Vector retrieval will complement, rather than replace, the relational database.

---

## 13. Machine Learning Requirements

The project will include machine-learning components related to financial risk intelligence.

Potential analytical capabilities include:

- market anomaly detection;
- volatility/risk-related prediction;
- derived financial features;
- model evaluation;
- temporal train/validation/test separation;
- storage of model outputs.

Machine-learning outputs shall be stored with sufficient metadata to identify the model, timestamp and associated entity.

---

## 14. AI Requirements

The AI layer shall operate on retrieved evidence and structured information.

The system should:

1. receive an analytical query;
2. retrieve relevant structured information;
3. retrieve relevant textual evidence;
4. retrieve relevant analytical/model outputs;
5. construct an evidence package;
6. generate an explanation based on the available evidence.

The AI layer should not be positioned as an autonomous financial decision-maker.

---

## 15. Security Requirements

The system shall consider:

- authentication;
- authorization;
- role-based access;
- input validation;
- secure password handling;
- protected API endpoints;
- protection against SQL injection through parameterized database access;
- appropriate handling of sensitive application information.

---

## 16. Database Design Requirements

The database design process shall follow:

Requirements
→ Entity Identification
→ Attribute Identification
→ Relationship Identification
→ Cardinality
→ ER Diagram
→ Relational Schema
→ Functional Dependencies
→ Normalization
→ PostgreSQL Implementation

The final database design shall be justified using the project's actual requirements.

---

## 17. Application Architecture

The planned architecture consists of:

- PostgreSQL for structured relational data;
- pgvector for semantic retrieval;
- FastAPI for backend/ML services;
- Next.js and TypeScript for the frontend;
- Python-based ML components;
- an AI layer for evidence-grounded explanations.

The architecture will maintain separation between data storage, analytical services, application APIs and presentation.

---

## 18. Testing Requirements

The project shall include testing for:

- database constraints;
- SQL queries;
- CRUD operations;
- API endpoints;
- authentication;
- ML components;
- semantic retrieval;
- frontend functionality;
- integration between components.

---

## 19. Git and Team Collaboration

The project shall be maintained using Git and GitHub.

Each team member shall make identifiable contributions through meaningful commits.

Major development work shall use feature branches and pull requests where appropriate.

Examples of contribution categories include:

- database design;
- SQL implementation;
- ML;
- backend/API;
- frontend;
- testing;
- documentation.

---

## 20. Success Criteria

The project will be considered successful when:

1. The ER model accurately represents the identified requirements.
2. The ER model is correctly converted into a relational schema.
3. The relational schema is appropriately normalized.
4. PostgreSQL contains the implemented schema and constraints.
5. Required SQL and advanced DBMS operations are demonstrated.
6. The database integrates with the application.
7. ML components generate reproducible analytical outputs.
8. Vector retrieval provides relevant evidence.
9. AI explanations are grounded in retrieved evidence.
10. The frontend provides a usable interface.
11. Authentication and security requirements are implemented appropriately.
12. GitHub history demonstrates contributions from both team members.
13. The complete system can be demonstrated and explained during evaluation.