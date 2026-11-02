import numpy as np
import pandas as pd
import pytest

from ml.train_models import FEATURES, build_features


def sample_prices(n=80):
    dates = pd.bdate_range("2024-01-01", periods=n)
    close = 100 * np.cumprod(1 + np.linspace(-0.002, 0.003, n))
    return pd.DataFrame({
        "security_id": 1, "ticker": "TEST", "observation_date": dates,
        "close": close, "high": close * 1.01, "low": close * 0.99,
        "volume": np.arange(n) + 1000,
    })


def test_feature_engineering_has_expected_features_and_future_target():
    result = build_features(sample_prices())
    assert set(FEATURES).issubset(result.columns)
    assert result["target_forward_volatility_5d"].notna().sum() > 0
    assert result["volatility_20d"].notna().sum() > 0


def test_forward_target_is_missing_at_end_of_series():
    result = build_features(sample_prices())
    assert result["target_forward_volatility_5d"].tail(5).isna().all()


def test_rejects_missing_market_columns():
    with pytest.raises(ValueError, match="Missing market columns"):
        build_features(pd.DataFrame({"close": [1, 2]}))
