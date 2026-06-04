"""FRAMA — Fractal Adaptive Moving Average: golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.frama import frama  # noqa: F401  (import fires @register for create())


def test_linear_ramp_tracks_close_exactly():
    # On a constant-slope ramp both half-window ranges and the full-window range are constant,
    # giving D ~= 0.92 -> alpha = exp(-4.6*(D-1)) ~= 1.43 -> clips to 1.0 -> FRAMA == close.
    ramp = np.arange(1.0, 61.0)
    out = INDICATORS.create("frama", length=16, batch=10).compute(frame(ramp))["frama"]
    np.testing.assert_allclose(out.iloc[20:].to_numpy(), ramp[20:], atol=1e-9)


def test_seed_passes_raw_close_before_window():
    # The first 2*batch bars are the recursion seed and equal the raw close untouched.
    ramp = np.arange(1.0, 61.0)
    out = INDICATORS.create("frama", length=16, batch=10).compute(frame(ramp))["frama"]
    np.testing.assert_allclose(out.iloc[:20].to_numpy(), ramp[:20], atol=1e-12)


def test_short_frame_is_all_seed():
    # Frame shorter than the full window (2*batch=20) never recurses -> output is the raw close.
    c = [float(i) for i in range(1, 11)]
    out = INDICATORS.create("frama", batch=10).compute(frame(c))["frama"]
    np.testing.assert_allclose(out.to_numpy(), c, atol=1e-12)


def test_flat_series_seed_then_nan():
    # A flat window collapses every range to 0 -> log(0) -> D NaN -> NaN from bar 2*batch on.
    # The seed region stays at the constant; we do NOT fabricate a pass-through (matches finta).
    out = INDICATORS.create("frama", batch=10).compute(frame([5.0] * 40))["frama"]
    np.testing.assert_allclose(out.iloc[:20].to_numpy(), 5.0, atol=1e-12)
    assert out.iloc[20:].isna().all()


def test_output_contract_and_bounds():
    df = deterministic_frame(200)
    out = INDICATORS.create("frama").compute(df)
    assert list(out.columns) == ["frama"]
    assert out["frama"].dtype == np.float64
    assert len(out) == len(df)
    # FRAMA is a convex blend of closes (alpha in [0.01,1]) -> stays within the close range.
    v = out["frama"].to_numpy()
    c = df["close"].to_numpy()
    fin = np.isfinite(v)
    assert fin.sum() > 100
    assert v[fin].min() >= c.min() - 1e-9
    assert v[fin].max() <= c.max() + 1e-9


def test_finite_and_varies_on_real_trend():
    out = INDICATORS.create("frama").compute(deterministic_frame(200))["frama"]
    v = out.dropna().to_numpy()
    assert v.size > 100 and v.std() > 0


def test_odd_length_rejected():
    with pytest.raises(ValueError, match="even"):
        frama(pd.Series([1.0, 2.0, 3.0]), length=15)


def test_default_length_is_sixteen():
    assert INDICATORS.create("frama").params["length"] == 16
