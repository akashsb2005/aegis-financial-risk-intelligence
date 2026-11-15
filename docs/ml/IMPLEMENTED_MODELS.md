# AEGIS market ML models

## Models

1. **Isolation Forest anomaly detector**: unsupervised outlier signal over daily return, rolling volatility, momentum, intraday range and volume deviation.
2. **Random Forest forward-volatility regressor**: predicts the next five-session realized volatility from features available at the prediction date.

Both are research/decision-support signals, not investment advice.

## Data and leakage controls

Input comes from `market_observations` joined to active `securities`. Features are computed independently per security after chronological sorting. The volatility target is derived from the next five sessions and is excluded from model inputs. Evaluation uses a chronological 80/20 date split; no random split is used. A constant training-mean baseline is reported alongside MAE, RMSE and R².

At least 100 usable rows and 10 distinct dates are required. Real market history must be ingested first; synthetic demo financial statements are not training labels. The current dataset is a limited demonstration universe, so metrics must not be generalized to the market.

## Run

```powershell
pip install -r ml/requirements.txt
$env:AEGIS_PG_DSN = "postgresql://USER:PASSWORD@localhost:5432/DBNAME"
python -m ml.train_models
```

The database must have core schema, `02_market_evidence.sql`, securities and sufficient market observations. Models and metrics are written under `ml/artifacts/` (ignored by Git); latest per-security anomaly and volatility signals are upserted to `model_predictions`.

## Reproducibility

Random states are fixed. The model code, feature list, version, chronological split and metrics are saved. Live market data retrieval is not part of model training or CI. Unit tests use deterministic fixture data. Re-run training after ingesting additional observations and compare against the baseline before interpreting outputs.

## Limitations

The anomaly model is unsupervised and does not prove fraud or misconduct. Forward volatility is a noisy statistical estimate, not a future price or loss prediction. No confidence interval, calibrated probability or causal interpretation is claimed.
