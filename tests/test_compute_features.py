"""build_features: indicator specs -> parametrized columns joined onto the frame."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators import build_features


def _frame(close):
    close = np.asarray(close, dtype="float64")
    n = len(close)
    ts = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    return pd.DataFrame({"ts": ts, "open": close, "high": close * 1.01, "low": close * 0.99,
                         "close": close, "close_raw": close, "volume": 1e6, "adj_factor": 1.0})


def test_build_features_joins_parametrized_columns():
    df = _frame(np.linspace(10, 50, 60))
    out = build_features(df, ["sma:period=10", "sma:period=20", {"name": "rsi", "params": {"period": 14}}])
    assert {"sma_10", "sma_20", "rsi_14"} <= set(out.columns)
    assert len(out) == len(df) and out.index.equals(df.index)
    # original OHLCV columns preserved
    assert {"ts", "open", "high", "low", "close", "volume"} <= set(out.columns)
    # build_features must not mutate the input
    assert "sma_10" not in df.columns


def test_build_features_injects_benchmark_for_relative_indicator():
    df = _frame(np.linspace(10, 50, 30))
    bench = pd.Series(np.linspace(5, 10, 30))
    out = build_features(df, ["rs_line:benchmark=SPY"], benchmark_close=bench)
    np.testing.assert_allclose(out["rs_line"].to_numpy(), df["close"].to_numpy() / bench.to_numpy())


def test_build_features_without_benchmark_is_degenerate():
    df = _frame(np.linspace(10, 50, 30))
    out = build_features(df, ["rs_line"])  # no benchmark -> ratio 1.0
    np.testing.assert_allclose(out["rs_line"].to_numpy(), 1.0)
