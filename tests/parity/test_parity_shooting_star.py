"""Shooting Star parity — EXACT integer match vs ``talib.CDLSHOOTINGSTAR`` (synthetic + real).

Candle patterns are integer-valued (here -100 or 0); parity is bit-exact with no tolerance, so
this uses ``assert_array_equal`` over the full series (TA-Lib's lookback warm-up is also 0 in our
output, so the regions align bar-for-bar).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.shooting_star import shooting_star  # noqa: F401  (fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("shooting_star").compute(df)["shooting_star"].to_numpy()
    ref = talib.CDLSHOOTINGSTAR(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_shooting_star_parity_synthetic():
    _check(deterministic_frame())


def test_shooting_star_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLSHOOTINGSTAR(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the real fixture actually exercises the pattern
    _check(df)
