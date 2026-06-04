"""Derivative Oscillator (Constance Brown) — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame

# Import the module directly so @INDICATORS.register fires for self-contained runs.
from pyindicators import INDICATORS
from pyindicators.momentum.derivative_osc import derivative_osc  # noqa: F401


def test_dosc_rising_line_is_zero():
    # On a strictly rising line RSI is pinned at 100; an EMA-of-EMA of a constant is that
    # constant, and so is its SMA -> smoothed == signal == 100 and dosc == 0 everywhere.
    out = INDICATORS.create("derivative_osc").compute(frame(np.arange(1.0, 80.0)))
    np.testing.assert_allclose(out["do_smoothed"].dropna().to_numpy(), 100.0, atol=1e-9)
    np.testing.assert_allclose(out["do_signal"].dropna().to_numpy(), 100.0, atol=1e-9)
    np.testing.assert_allclose(out["derivative_osc"].dropna().to_numpy(), 0.0, atol=1e-9)


def test_dosc_falling_line_is_zero():
    # Mirror image: a strictly falling line pins RSI at 0, so dosc collapses to 0 too.
    out = INDICATORS.create("derivative_osc").compute(frame(np.arange(80.0, 1.0, -1.0)))
    np.testing.assert_allclose(out["do_smoothed"].dropna().to_numpy(), 0.0, atol=1e-9)
    np.testing.assert_allclose(out["derivative_osc"].dropna().to_numpy(), 0.0, atol=1e-9)


def test_dosc_columns_present():
    out = INDICATORS.create("derivative_osc").compute(deterministic_frame(120))
    assert list(out.columns) == ["derivative_osc", "do_smoothed", "do_signal"]


def test_dosc_histogram_is_smoothed_minus_signal():
    # Structural identity: the published oscillator is exactly smoothed - signal.
    out = INDICATORS.create("derivative_osc").compute(deterministic_frame(200))
    np.testing.assert_allclose(
        out["derivative_osc"].to_numpy(),
        (out["do_smoothed"] - out["do_signal"]).to_numpy(),
        rtol=0,
        atol=0,
        equal_nan=True,
    )


def test_dosc_varies_on_real_trend():
    out = INDICATORS.create("derivative_osc").compute(deterministic_frame(300))["derivative_osc"]
    v = out.dropna().to_numpy()
    assert v.size > 100 and v.std() > 0.0  # oscillates, not stuck flat


def test_dosc_flat_input_all_nan():
    # Constant price -> RSI is 0/0 -> NaN, which propagates through every stage.
    out = INDICATORS.create("derivative_osc").compute(frame([42.0] * 120))
    assert out["derivative_osc"].isna().all()
    assert out["do_smoothed"].isna().all()
    assert out["do_signal"].isna().all()


def test_dosc_short_frame_all_nan():
    out = INDICATORS.create("derivative_osc").compute(frame([1.0, 2.0, 3.0, 4.0, 5.0]))
    assert out["derivative_osc"].isna().all()


def test_dosc_output_length_matches_input():
    df = deterministic_frame(150)
    out = INDICATORS.create("derivative_osc").compute(df)
    assert len(out) == len(df)
    assert out.to_numpy().dtype == np.float64
