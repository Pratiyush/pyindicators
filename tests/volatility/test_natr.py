"""NATR — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_flat_market_is_zero():
    f = frame([5.0] * 20, high=[5.0] * 20, low=[5.0] * 20)
    np.testing.assert_allclose(INDICATORS.create("natr", length=5).compute(f)["natr"].iloc[5:], 0.0)


def test_value_is_percent_of_close():
    # ATR = 2, close = 10 -> NATR = 100 * 2 / 10 = 20
    f = frame([10.0] * 20, high=[11.0] * 20, low=[9.0] * 20)
    np.testing.assert_allclose(INDICATORS.create("natr", length=5).compute(f)["natr"].iloc[4:], 20.0)
