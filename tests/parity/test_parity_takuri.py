"""Takuri parity — EXACT integer match vs ``talib.CDLTAKURI`` (synthetic + real).

Candle patterns are integer-valued (-100/0/100); parity is bit-exact with no tolerance, so
this uses ``assert_array_equal`` over the full series. TA-Lib's lookback warm-up (10 bars) is
also 0 in our output, so the regions align bar-for-bar.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.takuri import takuri  # noqa: F401  (fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("takuri").compute(df)["takuri"].to_numpy()
    ref = talib.CDLTAKURI(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_takuri_parity_synthetic():
    _check(deterministic_frame())


def test_takuri_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
