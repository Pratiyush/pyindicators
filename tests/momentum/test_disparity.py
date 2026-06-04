"""Disparity Index — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_constant_is_zero():
    out = INDICATORS.create("disparity_index", length=5).compute(frame([7.0] * 12))["disparity_index"]
    np.testing.assert_allclose(out.iloc[4:], 0.0, atol=1e-12)


def test_uptrend_positive():
    out = INDICATORS.create("disparity_index", length=5).compute(frame(np.arange(1, 20.0)))
    assert out["disparity_index"].iloc[-1] > 0  # price above its MA
