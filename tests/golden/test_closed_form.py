"""Closed-form golden tests — analytic cases that need no external data and pin the
exact math (including warm-up boundaries). These are the always-on correctness anchor.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators import INDICATORS


def frame(close, *, high=None, low=None, open_=None, volume=None) -> pd.DataFrame:
    close = np.asarray(close, dtype="float64")
    n = len(close)
    high = close if high is None else np.asarray(high, "float64")
    low = close if low is None else np.asarray(low, "float64")
    open_ = close if open_ is None else np.asarray(open_, "float64")
    volume = np.ones(n) if volume is None else np.asarray(volume, "float64")
    ts = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    return pd.DataFrame(
        {"ts": ts, "open": open_, "high": high, "low": low, "close": close,
         "close_raw": close, "volume": volume, "adj_factor": 1.0}
    )


def test_sma_of_constant_is_constant():
    out = INDICATORS.create("sma", period=5).compute(frame([7.0] * 12))
    assert out["sma"].iloc[:4].isna().all()  # warm-up = period - 1
    np.testing.assert_allclose(out["sma"].iloc[4:], 7.0)


def test_sma_of_linear_ramp_is_exact():
    a, b, n, p = 10.0, 2.0, 20, 5
    t = np.arange(n)
    out = INDICATORS.create("sma", period=p).compute(frame(a + b * t))
    # mean of close[t-4..t] of a linear ramp == a + b*(t - (p-1)/2)
    expected = a + b * (t - (p - 1) / 2)
    np.testing.assert_allclose(out["sma"].iloc[p - 1:], expected[p - 1:], rtol=1e-12)


def test_ema_of_constant_is_constant():
    out = INDICATORS.create("ema", period=4).compute(frame([3.0] * 10))
    np.testing.assert_allclose(out["ema"].iloc[3:], 3.0)


def test_rsi_monotone_extremes():
    up = INDICATORS.create("rsi", period=5).compute(frame(np.arange(1, 30, dtype=float)))
    np.testing.assert_allclose(up["rsi"].iloc[6:], 100.0)
    down = INDICATORS.create("rsi", period=5).compute(frame(np.arange(30, 1, -1, dtype=float)))
    np.testing.assert_allclose(down["rsi"].iloc[6:], 0.0)


def test_roc_of_constant_is_zero():
    out = INDICATORS.create("roc", period=3).compute(frame([5.0] * 8))
    np.testing.assert_allclose(out["roc"].iloc[3:], 0.0)


def test_rolling_high_low_on_ramp():
    n, w = 10, 3
    close = np.arange(1, n + 1, dtype=float)
    hi = INDICATORS.create("rolling_high", window=w).compute(frame(close))
    lo = INDICATORS.create("rolling_low", window=w).compute(frame(close))
    # increasing ramp: trailing max == current; trailing min == value (w-1) bars back
    np.testing.assert_allclose(hi["rolling_high"].iloc[w - 1:], close[w - 1:])
    np.testing.assert_allclose(lo["rolling_low"].iloc[w - 1:], close[: n - w + 1])


def test_atr_flat_market_is_zero():
    out = INDICATORS.create("atr", period=3).compute(frame([5.0] * 10))
    np.testing.assert_allclose(out["atr"].iloc[3:], 0.0)
    np.testing.assert_allclose(out["tr"].iloc[1:], 0.0)


def test_obv_known_sequence():
    out = INDICATORS.create("obv").compute(
        frame([1.0, 2.0, 3.0, 2.0, 2.0], volume=[10, 10, 10, 10, 10])
    )
    # diffs: 0(seed), +, +, -, 0  -> signed vol 0,10,10,-10,0 -> cumsum
    np.testing.assert_allclose(out["obv"].to_numpy(), [0.0, 10.0, 20.0, 10.0, 10.0])
