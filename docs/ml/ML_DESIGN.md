# AEGIS Machine Learning Design

## 1. Status

This document describes a proposed machine-learning workflow. The tracked repository currently contains database structures for storing risk assessments, but it does not contain a trained model, feature-engineering pipeline, model-serving endpoint, or model evaluation results. No predictive performance is claimed.

## 2. Objective

The intended ML component will generate explainable risk signals for a company using validated financial and other permitted observations. The output is decision support, not guaranteed financial advice or an autonomous investment recommendation.

## 3. Proposed workflow

1. Extract company and financial observations from PostgreSQL.
2. Validate completeness, ranges, units, fiscal periods, and data provenance.
3. Build a point-in-time feature set to avoid leakage from future information.
4. Split data by time and, where appropriate, by company to reduce leakage.
5. Train a transparent baseline model before evaluating more complex models.
6. Evaluate classification/regression performance and calibration.
7. Record model version, feature version, evaluation date, and limitations.
8. Generate a risk score and interpretable explanation.
9. Insert a new row into `risk_assessment`; do not overwrite historical assessments.

## 4. Candidate features

Potential features, subject to data availability and validation:

- Revenue and revenue growth
- Net profit and profit margin
- Total assets and liabilities
- Debt and leverage ratios
- Shareholders' equity
- Operating cash flow
- Historical risk score and score trend, using only prior assessments

Feature definitions, missing-value treatment, and calculation windows must be documented before training.

## 5. Baseline model strategy

Start with a simple, interpretable baseline appropriate to the available labels and sample size. Candidate approaches include logistic regression for labelled risk categories or a regression model for a continuous target. Model selection must be based on a defensible target definition and a representative dataset; do not train on synthetic labels and present the results as real-world performance.

## 6. Evaluation

For classification, report precision, recall, F1-score, confusion matrix, and class balance. For a continuous score, report MAE/RMSE and calibration or ranking analysis as appropriate. Use time-aware validation where the data has temporal structure.

Document dataset source, sample size, date range, split method, baseline, metrics, and limitations.

## 7. Database integration

The current `risk_assessment` relation stores company, score, risk level, assessment time, model version, explanation, and assessor. The database includes an insertion audit trigger and append-only protection.

The model service should validate outputs before insertion. Store enough provenance to reproduce or explain each result. Any additional model-run or feature tables require a separately reviewed schema change.

## 8. Responsible use

- Do not represent model output as certainty.
- Explain important contributing factors and data limitations.
- Monitor data drift and model performance.
- Avoid leakage and unsupported causal claims.
- Protect confidential financial and personal data.
- Keep a human decision-maker in the loop.

## 9. Completion criteria

The ML component is complete only when source code, reproducible training/evaluation steps, a documented dataset, measured results, model versioning, and a tested database integration are committed. Until then, this file remains a design document.
