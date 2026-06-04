"""Laguerre RSI — closed-form golden + edge cases.

No clean single-purpose oracle for the [0, 1] Ehlers scale, so the golden values are derived
by stepping the explicit L0..L3 recursion by hand on a tiny known sequence (see the comment
block on ``test_golden_closed_form``); parity vs pandas-ta's 0..100 ``lrsi`` lives in the
parity suite.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.momentum.laguerre_rsi import laguerre_rsi  # noqa: F401  (fires @register)


def test_golden_closed_form():
    # close = [10, 11, 12], gamma = 0.5. Stepping the cascade (all stages seeded at 10):
    #   bar1: L0=10.5,  L1=9.75,   L2=10.125, L3=9.9375
    #         CU = (10.5-9.75) + max(9.75-10.125,0) + max(10.125-9.9375,0) = 0.75+0+0.1875
    #         CD = 0 + (10.125-9.75) + 0 = 0.375  ->  0.9375 / 1.3125 = 5/7
    #   bar2: L0=11.25, L1=9.75,   L2=9.9375, L3=10.125
    #         CU = 1.5,  CD = 0.375              ->  1.5 / 1.875 = 0.8
    out = INDICATORS.create("laguerre_rsi", gamma=0.5).compute(frame([10.0, 11.0, 12.0]))
    vals = out["laguerre_rsi"].to_numpy()
    np.testing.assert_allclose(vals, [0.0, 5.0 / 7.0, 0.8], rtol=0, atol=1e-12)


def test_output_contract_and_bounds():
    out = INDICATORS.create("laguerre_rsi").compute(deterministic_frame(400))
    assert list(out.columns) == ["laguerre_rsi"]
    assert out["laguerre_rsi"].dtype == np.float64
    assert len(out) == 400
    v = out["laguerre_rsi"].to_numpy()
    assert np.isfinite(v).all()  # no warm-up NaNs: the cascade is seeded on bar 0
    assert (v >= 0.0).all() and (v <= 1.0).all()
    assert v.std() > 0  # actually varies on a real-ish walk


def test_constant_series_is_zero():
    # A flat cascade has CU == CD == 0 -> reported as 0.0 (no directional pressure), not NaN.
    out = INDICATORS.create("laguerre_rsi").compute(frame([42.0] * 50))
    v = out["laguerre_rsi"].to_numpy()
    assert np.isfinite(v).all()
    np.testing.assert_array_equal(v, np.zeros(50))


def test_pure_uptrend_saturates_high():
    out = INDICATORS.create("laguerre_rsi", gamma=0.5).compute(frame(np.arange(1.0, 60.0)))
    v = out["laguerre_rsi"].to_numpy()
    assert v[-1] == 1.0  # monotone rise -> every stage gap positive -> CD == 0 -> 1.0
    np.testing.assert_allclose(v[-10:], 1.0, atol=1e-12)


def test_pure_downtrend_saturates_low():
    out = INDICATORS.create("laguerre_rsi", gamma=0.5).compute(frame(np.arange(60.0, 1.0, -1.0)))
    v = out["laguerre_rsi"].to_numpy()
    assert v[-1] == 0.0  # monotone fall -> CU == 0 -> 0.0
    np.testing.assert_allclose(v[-10:], 0.0, atol=1e-12)


def test_short_and_single_bar_frames():
    # Single bar: just the seed (flat cascade) -> 0.0, length preserved, no error.
    one = INDICATORS.create("laguerre_rsi").compute(frame([5.0]))["laguerre_rsi"]
    assert len(one) == 1 and one.iloc[0] == 0.0
    two = INDICATORS.create("laguerre_rsi").compute(frame([5.0, 6.0]))["laguerre_rsi"]
    assert len(two) == 2 and np.isfinite(two.to_numpy()).all()


def test_gamma_changes_responsiveness():
    # Lower gamma tracks price more tightly, so on the same series the two settings differ.
    df = deterministic_frame(300)
    fast = INDICATORS.create("laguerre_rsi", gamma=0.2).compute(df)["laguerre_rsi"].to_numpy()
    slow = INDICATORS.create("laguerre_rsi", gamma=0.8).compute(df)["laguerre_rsi"].to_numpy()
    assert np.nanmax(np.abs(fast - slow)) > 1e-3
    for v in (fast, slow):
        assert (v >= 0.0).all() and (v <= 1.0).all()


def test_function_matches_registry():
    df = deterministic_frame(120)
    direct = laguerre_rsi(df["close"], gamma=0.5).to_numpy()
    viareg = INDICATORS.create("laguerre_rsi", gamma=0.5).compute(df)["laguerre_rsi"].to_numpy()
    np.testing.assert_allclose(direct, viareg, rtol=0, atol=0)


def test_rejects_unknown_param():
    import pytest

    with pytest.raises(Exception):  # noqa: B017 (pydantic ValidationError on extra='forbid')
        INDICATORS.create("laguerre_rsi", length=14)


def test_empty_series():
    import pandas as pd

    assert laguerre_rsi(pd.Series([], dtype="float64")).empty  # n == 0 guard
