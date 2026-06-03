"""Stochastic — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_rising_close_at_top_is_100():
    c = np.arange(1, 30.0)
    out = INDICATORS.create("stoch").compute(frame(c, high=c, low=c - 1))
    np.testing.assert_allclose(out["stoch_k"].dropna().iloc[-5:], 100.0)


def test_flat_window_is_nan():
    out = INDICATORS.create("stoch").compute(frame([5.0] * 40, high=[5.0] * 40, low=[5.0] * 40))
    assert out["stoch_k"].isna().all()
