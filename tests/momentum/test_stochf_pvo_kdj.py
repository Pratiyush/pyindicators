"""Fast Stochastic / PVO / KDJ — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_stochf_flat_window_is_nan():
    out = INDICATORS.create("stochf").compute(frame([5.0] * 30))
    assert out["stochf_k"].isna().all()  # HH == LL -> %K undefined


def test_stochf_close_at_high_is_100():
    # close sits at the top of every window -> raw %K == 100
    n = 20
    close = np.full(n, 10.0)
    out = INDICATORS.create("stochf", k=5, d=3).compute(
        frame(close, high=close, low=close - 2.0)
    )["stochf_k"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 100.0)


def test_stochf_bounds():
    out = INDICATORS.create("stochf").compute(deterministic_frame(200))
    for col in ("stochf_k", "stochf_d"):
        v = out[col].dropna().to_numpy()
        assert v.min() >= -1e-9 and v.max() <= 100.0 + 1e-9


def test_pvo_constant_volume_is_zero():
    out = INDICATORS.create("pvo").compute(frame([10.0] * 80, volume=[1000.0] * 80))
    for col in ("pvo", "pvo_signal", "pvo_hist"):
        np.testing.assert_allclose(out[col].dropna().to_numpy(), 0.0, atol=1e-9)


def test_pvo_positive_when_volume_expands():
    vol = np.concatenate([np.full(40, 100.0), np.full(40, 1000.0)])
    out = INDICATORS.create("pvo").compute(frame([10.0] * 80, volume=vol))["pvo"]
    assert out.iloc[-1] > 0  # fast EMA of volume above slow EMA


def test_kdj_j_is_three_k_minus_two_d():
    out = INDICATORS.create("kdj").compute(deterministic_frame(120))
    j = out["kdj_j"].to_numpy()
    expected = 3.0 * out["kdj_k"].to_numpy() - 2.0 * out["kdj_d"].to_numpy()
    np.testing.assert_allclose(j, expected, equal_nan=True)


def test_kdj_flat_window_is_nan():
    out = INDICATORS.create("kdj").compute(frame([5.0] * 30))
    assert out["kdj_k"].isna().all()
