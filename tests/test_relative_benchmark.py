"""Relative-strength indicators with an injected benchmark (the screener's path)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS


def test_rs_line_uses_injected_benchmark():
    df = deterministic_frame(n=50)
    bench = pd.Series(np.linspace(50.0, 80.0, len(df)))
    ind = INDICATORS.get("rs_line")(benchmark_close=bench)
    out = ind.compute(df)
    expected = df["close"].to_numpy() / bench.to_numpy()
    np.testing.assert_allclose(out["rs_line"].to_numpy(), expected, rtol=1e-12)


def test_rs_line_degenerate_without_benchmark():
    df = deterministic_frame(n=20)
    out = INDICATORS.create("rs_line").compute(df)
    np.testing.assert_allclose(out["rs_line"].to_numpy(), 1.0)


def test_benchmark_length_mismatch_raises():
    df = deterministic_frame(n=30)
    ind = INDICATORS.get("rs_line")(benchmark_close=pd.Series([1.0, 2.0, 3.0]))
    with pytest.raises(ValueError):
        ind.compute(df)


def test_mansfield_rs_with_benchmark_is_finite_after_warmup():
    df = deterministic_frame(n=120)
    bench = pd.Series(np.linspace(50.0, 80.0, len(df)))
    ind = INDICATORS.get("mansfield_rs")(period=10, benchmark_close=bench)
    out = ind.compute(df)
    assert out["mansfield_rs"].iloc[:9].isna().all()  # period-1 warm-up
    assert np.isfinite(out["mansfield_rs"].iloc[-1])
