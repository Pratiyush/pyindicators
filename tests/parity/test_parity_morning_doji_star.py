"""Morning Doji Star parity — EXACT integer match vs ``talib.CDLMORNINGDOJISTAR``.

Candles are integer-exact (-100/0/100), so parity is asserted with no tolerance via
``np.testing.assert_array_equal`` on the synthetic deterministic frame and the genuine AAPL
daily fixture. This pattern is rare and does not fire on either of those frames (both stay all
zero), so a third, hand-constructed firing frame is included to exercise the +100 hit path
against TA-Lib as well — otherwise parity would only cover the all-zero default.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.morning_doji_star import (
    morning_doji_star,  # noqa: F401  (fires @register)
)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("morning_doji_star").compute(df)["morning_doji_star"].to_numpy()
    ref = talib.CDLMORNINGDOJISTAR(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _firing_frame():
    # Long black (110->100), a doji gapping down (open=close=95), then a white candle closing
    # deep into the first black body (96->108) -> a genuine Morning Doji Star (+100) at bar 14.
    warm = 12
    o = [100.0] * warm + [110.0, 95.0, 96.0]
    c = [102.0] * warm + [100.0, 95.0, 108.0]
    h = [102.2] * warm + [110.5, 95.5, 108.5]
    low = [99.8] * warm + [99.5, 94.5, 95.5]
    return frame(c, high=h, low=low, open_=o)


def test_morning_doji_star_parity_synthetic():
    _check(deterministic_frame())


def test_morning_doji_star_parity_real():
    _check(real_frame())  # genuine AAPL daily bars (pattern does not fire; all-zero path)


def test_morning_doji_star_parity_firing():
    df = _firing_frame()
    ref = talib.CDLMORNINGDOJISTAR(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the constructed frame genuinely triggers the bullish pattern
    _check(df)
