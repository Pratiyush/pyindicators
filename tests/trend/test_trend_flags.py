"""Increasing, Decreasing, TTM Trend — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_increasing_and_decreasing_on_uptrend():
    up = frame(np.arange(1, 10.0))
    inc = INDICATORS.create("increasing", length=1).compute(up)["increasing"]
    dec = INDICATORS.create("decreasing", length=1).compute(up)["decreasing"]
    assert (inc.iloc[1:] == 1.0).all() and (dec.iloc[1:] == 0.0).all()


def test_decreasing_on_downtrend():
    down = frame(np.arange(10, 1, -1.0))
    dec = INDICATORS.create("decreasing", length=1).compute(down)["decreasing"]
    assert (dec.iloc[1:] == 1.0).all()


def test_ttm_trend_uptrend_is_positive():
    up = np.arange(1, 40.0)
    out = INDICATORS.create("ttm_trend").compute(frame(up, high=up, low=up))["ttm_trend"]
    assert out.dropna().iloc[-1] == 1.0
