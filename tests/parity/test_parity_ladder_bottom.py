"""Ladder Bottom parity — EXACT integer match vs ``talib.CDLLADDERBOTTOM``.

Checked on the synthetic walk and on genuine AAPL daily bars (no tolerance — candles are
integer-exact). The real fixtures never form a Ladder Bottom (all zeros), so a hand-built
five-bar frame additionally pins a real +100 emission, verifying parity on an actual pattern
hit and not only on the all-zero fixtures.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.ladder_bottom import ladder_bottom  # noqa: F401  (fires @register)

talib = pytest.importorskip("talib")

_LOOKBACK = 14


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("ladder_bottom").compute(df)["ladder_bottom"].to_numpy()
    ref = talib.CDLLADDERBOTTOM(*_ohlc(df)).astype("float64")
    ref[:_LOOKBACK] = 0.0  # force the lookback warm-up to 0 to match talib's outBegIdx offset
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _hit_frame():
    # 14 warm-up bars (HL range 4.0 -> ShadowVeryShort avg ~0.4) then five pattern bars: three
    # black candles with lower opens and lower closes, a fourth black candle with a long upper
    # shadow, then a white candle opening above the prior open and closing above the prior high.
    warm = 14
    o = [100.0] * warm + [120.0, 115.0, 110.0, 104.0, 105.0]
    c = [101.0] * warm + [112.0, 107.0, 102.0, 100.0, 110.0]
    h = [103.0] * warm + [120.3, 115.3, 110.3, 109.0, 110.3]
    low = [99.0] * warm + [111.7, 106.7, 101.7, 99.7, 104.7]
    return frame(c, high=h, low=low, open_=o)


def test_ladder_bottom_parity_synthetic():
    _check(deterministic_frame())


def test_ladder_bottom_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_ladder_bottom_parity_constructed_hit():
    df = _hit_frame()
    ref = talib.CDLLADDERBOTTOM(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the constructed frame actually triggers the pattern
    _check(df)
