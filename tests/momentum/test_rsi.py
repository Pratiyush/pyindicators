"""RSI — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_monotone_up_is_100():
    out = INDICATORS.create("rsi", length=5).compute(frame(np.arange(1, 30.0)))
    np.testing.assert_allclose(out["rsi"].iloc[6:], 100.0)


def test_monotone_down_is_0():
    out = INDICATORS.create("rsi", length=5).compute(frame(np.arange(30, 1, -1.0)))
    np.testing.assert_allclose(out["rsi"].iloc[6:], 0.0)


def test_flat_series_is_nan():
    out = INDICATORS.create("rsi", length=5).compute(frame([5.0] * 20))
    assert out["rsi"].iloc[6:].isna().all()
