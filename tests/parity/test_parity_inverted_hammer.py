"""Inverted Hammer parity — EXACT integer match vs ``talib.CDLINVERTEDHAMMER`` (synth + real).

Candle patterns are integer-valued (-100/0/100); parity is bit-exact with no tolerance, so
this uses ``assert_array_equal`` over the full series. TA-Lib forces its lookback warm-up to 0
and so do we, so the regions align bar-for-bar.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.inverted_hammer import inverted_hammer  # noqa: F401  (fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("inverted_hammer").compute(df)["inverted_hammer"].to_numpy()
    ref = talib.CDLINVERTEDHAMMER(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_inverted_hammer_parity_synthetic():
    _check(deterministic_frame())


def test_inverted_hammer_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
