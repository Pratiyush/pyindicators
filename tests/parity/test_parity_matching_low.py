"""Matching Low parity — EXACT integer match vs ``talib.CDLMATCHINGLOW`` (synthetic + real).

Candle patterns are integer-exact, so this asserts a bit-exact match with no tolerance on both
the deterministic random-walk frame and the genuine AAPL daily fixture. CDLMATCHINGLOW is
bullish-only: it emits just 0/100 (no negative value and no ±80 partial score), and its lookback
is 6 (first 6 bars forced to 0).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.matching_low import matching_low  # noqa: F401 (import fires @register)

talib = pytest.importorskip("talib")

_LOOKBACK = 6


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("matching_low").compute(df)["matching_low"].to_numpy()
    ref = talib.CDLMATCHINGLOW(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    # The first 'lookback' bars are forced to 0 to match TA-Lib's lookback handling.
    ref[:_LOOKBACK] = 0.0
    np.testing.assert_array_equal(our, ref)
    # Output is bullish-only pure 0/100 — never negative, never a partial ±80 score.
    assert set(np.unique(our)) <= {0.0, 100.0}


def test_matching_low_parity_synthetic():
    df = deterministic_frame()
    ref = talib.CDLMATCHINGLOW(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the synthetic frame actually exercises the pattern
    _check(df)


def test_matching_low_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLMATCHINGLOW(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the real fixture actually exercises the pattern
    _check(df)
