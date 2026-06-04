"""Counterattack parity — EXACT integer match vs ``talib.CDLCOUNTERATTACK`` (synthetic + real).

Candle patterns are integer-exact, so this asserts a bit-exact match with no tolerance on both
the deterministic random-walk frame and the genuine AAPL daily fixture. CDLCOUNTERATTACK emits
only -100/0/100 (no ±80 partial score), and its lookback is 11 (first 11 bars forced to 0).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.counterattack import counterattack  # noqa: F401 (import fires @register)

talib = pytest.importorskip("talib")

_LOOKBACK = 11


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("counterattack").compute(df)["counterattack"].to_numpy()
    ref = talib.CDLCOUNTERATTACK(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    # The first 'lookback' bars are forced to 0 to match TA-Lib's lookback handling.
    ref[:_LOOKBACK] = 0.0
    np.testing.assert_array_equal(our, ref)
    # Output is pure ±100/0 — never a partial ±80 score for this pattern.
    assert set(np.unique(our)) <= {-100.0, 0.0, 100.0}


def test_counterattack_parity_synthetic():
    _check(deterministic_frame())


def test_counterattack_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
