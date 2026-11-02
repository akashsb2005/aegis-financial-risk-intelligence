"""Train AEGIS anomaly and forward-volatility models from PostgreSQL market history.

No external API keys are required. Training requires sufficient real observations.
The models are research signals, not financial advice.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import psycopg
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

FEATURES = ["return_1d", "volatility_5d", "volatility_20d", "momentum_5d",
            "momentum_20d", "intraday_range", "volume_zscore"]
VERSION = "1.0.0"


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Build point-in-time features and a strictly future 5-session volatility target."""
    required = {"security_id", "ticker", "observation_date", "close", "volume", "high", "low"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing market columns: {sorted(missing)}")
    data = frame.copy()
    data["observation_date"] = pd.to_datetime(data["observation_date"])
    data = data.sort_values(["security_id", "observation_date"]).drop_duplicates(
        ["security_id", "observation_date"], keep="last"
    )
    data["close"] = pd.to_numeric(data["close"], errors="coerce")
    data["volume"] = pd.to_numeric(data["volume"], errors="coerce")
    data = data[data["close"] > 0].copy()
    grouped = data.groupby("security_id", sort=False)
    data["return_1d"] = grouped["close"].pct_change()
    data["volatility_5d"] = data.groupby("security_id")["return_1d"].transform(
        lambda x: x.rolling(5, min_periods=5).std()
    )
    data["volatility_20d"] = data.groupby("security_id")["return_1d"].transform(
        lambda x: x.rolling(20, min_periods=20).std()
    )
    data["momentum_5d"] = grouped["close"].pct_change(5)
    data["momentum_20d"] = grouped["close"].pct_change(20)
    data["intraday_range"] = (data["high"] - data["low"]) / data["close"]
    log_volume = np.log1p(data["volume"].clip(lower=0))
    data["volume_zscore"] = data.groupby("security_id")[log_volume.name].transform(
        lambda x: (x - x.rolling(20, min_periods=20).mean()) /
                  x.rolling(20, min_periods=20).std().replace(0, np.nan)
    ) if log_volume.name in data.columns else np.nan
    # Compute a 5-session forward realized volatility label. It is never an input feature.
    data["target_forward_volatility_5d"] = data.groupby("security_id")["return_1d"].transform(
        lambda x: x.shift(-1).rolling(5, min_periods=5).std().shift(-4)
    )
    return data.replace([np.inf, -np.inf], np.nan)


def load_market_data(dsn: str) -> pd.DataFrame:
    query = """
      SELECT s.security_id, s.ticker, m.observation_date, m.close,
             m.high, m.low, m.volume
      FROM public.market_observations m
      JOIN public.securities s USING (security_id)
      WHERE s.is_active = TRUE
      ORDER BY s.security_id, m.observation_date
    """
    with psycopg.connect(dsn) as conn:
        return pd.read_sql_query(query, conn)


def train_models(frame: pd.DataFrame, output_dir: Path) -> dict:
    data = build_features(frame)
    usable = data.dropna(subset=FEATURES + ["target_forward_volatility_5d"]).copy()
    if usable["security_id"].nunique() < 1 or len(usable) < 100:
        raise ValueError("Need at least 100 usable rows after rolling windows; ingest more history.")
    dates = np.sort(usable["observation_date"].unique())
    if len(dates) < 10:
        raise ValueError("Need at least 10 distinct observation dates for chronological evaluation.")
    cutoff = dates[int(len(dates) * 0.8)]
    train = usable[usable["observation_date"] < cutoff]
    test = usable[usable["observation_date"] >= cutoff]
    if len(train) < 50 or len(test) < 10:
        raise ValueError("Insufficient chronological train/test rows; ingest more history.")

    X_train, X_test = train[FEATURES], test[FEATURES]
    y_train = train["target_forward_volatility_5d"]
    y_test = test["target_forward_volatility_5d"]

    volatility_model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestRegressor(n_estimators=250, min_samples_leaf=3,
                                        max_features=0.8, random_state=42, n_jobs=-1)),
    ])
    volatility_model.fit(X_train, y_train)
    predicted = volatility_model.predict(X_test)
    metrics = {
        "rows": int(len(usable)), "train_rows": int(len(train)), "test_rows": int(len(test)),
        "train_end": str(train["observation_date"].max().date()),
        "test_start": str(test["observation_date"].min().date()),
        "mae": float(mean_absolute_error(y_test, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, predicted))),
        "r2": float(r2_score(y_test, predicted)),
        "baseline_mae": float(mean_absolute_error(y_test, np.repeat(y_train.mean(), len(y_test)))),
        "features": FEATURES, "target": "next 5-session realized volatility",
        "split": "chronological 80/20 by observation date",
    }

    anomaly_model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", IsolationForest(n_estimators=250, contamination="auto",
                                  random_state=42, n_jobs=-1)),
    ])
    anomaly_model.fit(usable[FEATURES])
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(volatility_model, output_dir / "volatility_model.joblib")
    joblib.dump(anomaly_model, output_dir / "anomaly_model.joblib")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    latest = data.dropna(subset=FEATURES).sort_values("observation_date").groupby(
        "security_id", as_index=False
    ).tail(1)
    latest["predicted_volatility"] = volatility_model.predict(latest[FEATURES])
    latest["anomaly_label"] = anomaly_model.predict(latest[FEATURES])
    latest["anomaly_score"] = anomaly_model.decision_function(latest[FEATURES])
    return {"metrics": metrics, "predictions": latest}


def persist_predictions(dsn: str, predictions: pd.DataFrame, metrics: dict) -> int:
    sql = """
      INSERT INTO public.model_predictions
        (security_id, prediction_type, prediction_date, target_date,
         predicted_value, signal, model_name, model_version, metrics, features)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb)
      ON CONFLICT (security_id,prediction_type,prediction_date,model_name,model_version)
      DO UPDATE SET predicted_value=EXCLUDED.predicted_value, signal=EXCLUDED.signal,
                    metrics=EXCLUDED.metrics, features=EXCLUDED.features, created_at=now()
    """
    rows = []
    for _, row in predictions.iterrows():
        day = pd.Timestamp(row["observation_date"]).date()
        feature_json = json.dumps({key: (None if pd.isna(row[key]) else float(row[key]))
                                   for key in FEATURES})
        rows.append((int(row["security_id"]), "VOLATILITY", day, None,
                     float(row["predicted_volatility"]), "FORECAST",
                     "random_forest_forward_volatility", VERSION,
                     json.dumps(metrics), feature_json))
        rows.append((int(row["security_id"]), "ANOMALY", day, None,
                     float(row["anomaly_score"]),
                     "ANOMALY" if int(row["anomaly_label"]) == -1 else "NORMAL",
                     "isolation_forest_market_anomaly", VERSION,
                     json.dumps({"contamination": "auto"}), feature_json))
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.executemany(sql, rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="ml/artifacts")
    parser.add_argument("--no-persist", action="store_true")
    args = parser.parse_args()
    dsn = os.environ.get("AEGIS_PG_DSN")
    if not dsn:
        raise SystemExit("Set AEGIS_PG_DSN to your PostgreSQL DSN.")
    result = train_models(load_market_data(dsn), Path(args.output))
    print(json.dumps(result["metrics"], indent=2))
    if not args.no_persist:
        print(f"Persisted {persist_predictions(dsn, result['predictions'], result['metrics'])} predictions.")


if __name__ == "__main__":
    main()
