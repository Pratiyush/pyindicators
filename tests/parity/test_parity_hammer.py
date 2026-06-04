"""Hammer parity — EXACT integer match vs ``talib.CDLHAMMER`` (synthetic + real).

CDLHAMMER emits only 0 or 100 (a bullish single-bar reversal; no negative or partial score),
so the match is bit-exact with no tolerance on both the deterministic walk and genuine AAPL
daily bars.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.hammer import hammer  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("hammer").compute(df)["hammer"].to_numpy()
    ref = talib.CDLHAMMER(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_hammer_parity_synthetic():
    _check(deterministic_frame())


def test_hammer_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLHAMMER(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the real fixture actually triggers the pattern
    _check(df)
