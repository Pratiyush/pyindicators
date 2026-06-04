"""Gap side-by-side white parity — EXACT integer match vs ``talib.CDLGAPSIDESIDEWHITE``.

Candlestick outputs are integer-exact (-100/0/100), so this asserts equality with **no**
tolerance on both the synthetic deterministic frame and the real AAPL daily fixture.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.gap_side_side_white import (  # noqa: F401  (import fires @register)
    gap_side_side_white,
)

talib = pytest.importorskip("talib")

_LOOKBACK = 7


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("gap_side_side_white").compute(df)["gap_side_side_white"].to_numpy()
    ref = talib.CDLGAPSIDESIDEWHITE(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    # Force the first 'lookback' bars to 0 on both sides (TA-Lib lookback warm-up).
    ref[:_LOOKBACK] = 0.0
    np.testing.assert_array_equal(our, ref)


def test_gap_side_side_white_parity_synthetic():
    _check(deterministic_frame())


def test_gap_side_side_white_parity_real():
    _check(real_frame())  # genuine AAPL daily bars (real gaps)
