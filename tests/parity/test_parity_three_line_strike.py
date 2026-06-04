"""Three-Line Strike parity — EXACT integer match vs ``talib.CDL3LINESTRIKE``.

Candles are integer-exact, so this asserts equality with no tolerance on both the synthetic
deterministic frame and genuine AAPL daily bars. The real fixture contains a genuine firing
of the pattern, so the comparison proves we match TA-Lib on real price action, not only on
the trivial all-zero case.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.three_line_strike import (
    three_line_strike,  # noqa: F401  (fires @register)
)

talib = pytest.importorskip("talib")

# TA-Lib lookback for CDL3LINESTRIKE (avgPeriod(Near) + 3); the first bars are always 0.
_LOOKBACK = 8


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("three_line_strike").compute(df)["three_line_strike"].to_numpy()
    ref = talib.CDL3LINESTRIKE(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    # Force the first 'lookback' bars to 0 to match TA-Lib's warm-up convention exactly.
    ref[:_LOOKBACK] = 0.0
    np.testing.assert_array_equal(our, ref)


def test_three_line_strike_parity_synthetic():
    _check(deterministic_frame())


def test_three_line_strike_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDL3LINESTRIKE(*_ohlc(df)).astype("float64")
    assert np.any(ref != 0)  # the real fixture contains a genuine three-line-strike firing
    _check(df)
