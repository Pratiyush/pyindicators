"""SMA Slope — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_constant_series_slope_zero():
    out = INDICATORS.create("sma_slope", length=5).compute(frame([5.0] * 12))["sma_slope"]
    np.testing.assert_allclose(out.iloc[5:], 0.0, atol=1e-12)


def test_uptrend_slope_positive():
    out = INDICATORS.create("sma_slope", length=5).compute(frame(np.arange(1, 20.0)))["sma_slope"]
    assert (out.dropna() > 0).all()
