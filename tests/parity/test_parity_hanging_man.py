"""Hanging Man parity — EXACT integer match vs ``talib.CDLHANGINGMAN`` (synthetic + real).

Candles are integer-exact (-100/0 here), so the comparison is ``assert_array_equal`` with no
tolerance. The uptrend confirmation (prior high within a ``Near`` tolerance of the current body
bottom) is exercised by the real AAPL fixture, which carries genuine -100 hits.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.hanging_man import hanging_man  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")

_LOOKBACK = 11


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("hanging_man").compute(df)["hanging_man"].to_numpy()
    ref = talib.CDLHANGINGMAN(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    # TA-Lib emits 0 for the first ``lookback`` bars; our output does too. Force-align to be
    # explicit that the warm-up is zero on both sides (no spurious early signals).
    np.testing.assert_array_equal(our[:_LOOKBACK], 0.0)
    np.testing.assert_array_equal(ref[:_LOOKBACK], 0.0)
    np.testing.assert_array_equal(our, ref)


def test_hanging_man_parity_synthetic():
    _check(deterministic_frame())


def test_hanging_man_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLHANGINGMAN(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the real fixture carries genuine bearish hanging-man hits
    _check(df)
