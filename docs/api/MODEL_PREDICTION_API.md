# Model prediction API

The authenticated endpoint `GET /api/v1/companies/{company_id}/predictions` reads persisted signals from `model_predictions`, joined through `securities` to enforce company scope.

Optional query parameters:
- `prediction_type=ANOMALY|VOLATILITY`
- `limit` (1–100, default 50)
- `offset` (default 0)

The response includes prediction date, security ticker/exchange, numeric value, signal, model name/version, metrics, feature snapshot and creation timestamp. Unauthenticated requests receive 401; unknown companies receive 404. This endpoint only reads stored predictions; it does not train models during a request. Run the ML training pipeline separately to populate the table.
