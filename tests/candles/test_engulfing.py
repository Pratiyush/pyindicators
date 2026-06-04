"""Engulfing — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.engulfing import engulfing  # noqa: F401  (import fires @register)


def _eng(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("engulfing").compute(df)["engulfing"].to_numpy()


def test_engulfing_bullish_strict():
    # bar1 black (100->99), bar2 white (98->101) strictly engulfs -> +100.
    out = _eng([100.0, 100.0, 98.0], [100.0, 100.5, 101.5], [100.0, 98.5, 97.5],
               [100.0, 99.0, 101.0])
    assert out[2] == 100.0


def test_engulfing_bearish_strict():
    # bar1 white (100->101), bar2 black (102->99) strictly engulfs -> -100.
    out = _eng([100.0, 100.0, 102.0], [100.0, 101.5, 102.5], [100.0, 99.5, 98.5],
               [100.0, 101.0, 99.0])
    assert out[2] == -100.0


def test_engulfing_one_edge_touch_is_80():
    # bar2 open == bar1 close (bottom touch) with a strict top -> partial score +80.
    out = _eng([100.0, 100.0, 99.0], [100.0, 100.5, 101.5], [100.0, 98.5, 98.5],
               [100.0, 99.0, 101.0])
    assert out[2] == 80.0


def test_engulfing_identical_body_is_zero():
    # Both edges equal (identical opposite bodies) is NOT engulfing -> 0.
    out = _eng([100.0, 100.0, 101.0], [100.0, 101.0, 101.0], [100.0, 100.0, 100.0],
               [100.0, 101.0, 100.0])
    assert out[2] == 0.0


def test_engulfing_lookback_zeros_first_two():
    out = _eng([100.0, 100.0, 98.0], [100.0, 100.5, 101.5], [100.0, 98.5, 97.5],
               [100.0, 99.0, 101.0])
    np.testing.assert_array_equal(out[:2], 0.0)  # TA-Lib lookback = 2
