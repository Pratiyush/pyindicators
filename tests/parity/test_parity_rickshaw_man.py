"""Rickshaw Man parity — EXACT integer match vs ``talib.CDLRICKSHAWMAN`` (synthetic + real).

Candle patterns are integer-valued (-100/0/100); parity is bit-exact with no tolerance, so
this uses ``assert_array_equal`` over the full series (TA-Lib's lookback warm-up is also 0 in
our output, so the regions align bar-for-bar).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.rickshaw_man import rickshaw_man  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")

# TA-Lib lookback for CDLRICKSHAWMAN = max(BodyDoji=10, ShadowLong=0, Near=5) = 10.
_LOOKBACK = 10


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("rickshaw_man").compute(df)["rickshaw_man"].to_numpy()
    ref = talib.CDLRICKSHAWMAN(*_ohlc(df)).astype("float64")
    ref[:_LOOKBACK] = 0.0  # force the first 'lookback' bars to 0 to align with our warm-up
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_rickshaw_man_parity_synthetic():
    _check(deterministic_frame())


def test_rickshaw_man_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
