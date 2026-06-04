"""Bias, PSL, ER, Slope, Elder Ray — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_bias_constant_zero_and_uptrend_positive():
    np.testing.assert_allclose(
        INDICATORS.create("bias", length=5).compute(frame([7.0] * 12))["bias"].iloc[4:], 0.0, atol=1e-12
    )
    up = INDICATORS.create("bias", length=5).compute(frame(np.arange(1, 30.0)))["bias"]
    assert up.iloc[-1] > 0  # price above its trailing mean


def test_psl_extremes():
    # Tail (after the bar-0 "not-up" leaves the window): all-up -> 100, all-down -> 0.
    up = INDICATORS.create("psl", length=5).compute(frame(np.arange(1, 20.0)))["psl"]
    np.testing.assert_allclose(up.iloc[-3:], 100.0)
    down = INDICATORS.create("psl", length=5).compute(frame(np.arange(20, 1, -1.0)))["psl"]
    np.testing.assert_allclose(down.dropna(), 0.0)


def test_er_straight_line_is_one():
    out = INDICATORS.create("er", length=5).compute(frame(np.arange(1, 30.0) * 2.0))["er"]
    np.testing.assert_allclose(out.dropna(), 1.0, atol=1e-12)  # perfectly efficient


def test_slope_of_linear():
    out = INDICATORS.create("slope", length=1).compute(frame(10.0 + 2.0 * np.arange(10.0)))["slope"]
    np.testing.assert_allclose(out.dropna(), 2.0)


def test_eri_outputs_finite():
    out = INDICATORS.create("eri").compute(deterministic_frame(60))
    assert np.isfinite(out["bull_power"].iloc[-1]) and np.isfinite(out["bear_power"].iloc[-1])
