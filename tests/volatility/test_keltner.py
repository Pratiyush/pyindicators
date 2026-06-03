"""Keltner Channels — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_flat_market_bands_collapse():
    out = INDICATORS.create("keltner", length=5, atr_length=5).compute(
        frame([5.0] * 30, high=[5.0] * 30, low=[5.0] * 30)
    )
    np.testing.assert_allclose(out["kc_middle"].dropna(), 5.0)
    np.testing.assert_allclose(out["kc_upper"].dropna(), 5.0)  # ATR 0
    np.testing.assert_allclose(out["kc_lower"].dropna(), 5.0)


def test_bands_ordered_when_volatile():
    c = np.arange(1, 40.0)
    out = INDICATORS.create("keltner").compute(frame(c, high=c + 1, low=c - 1))
    last = out.iloc[-1]
    assert last["kc_upper"] > last["kc_middle"] > last["kc_lower"]
