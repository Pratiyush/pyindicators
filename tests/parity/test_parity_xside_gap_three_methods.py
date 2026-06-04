"""Upside/Downside gap three methods parity — EXACT integer match vs talib.CDLXSIDEGAP3METHODS.

Candlestick outputs are integer-exact (-100/0/100), so this asserts equality with **no**
tolerance on both the synthetic deterministic frame and the real AAPL daily fixture.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.xside_gap_three_methods import (  # noqa: F401  (import fires @register)
    xside_gap_three_methods,
)

talib = pytest.importorskip("talib")

_LOOKBACK = 2


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    col = "xside_gap_three_methods"
    our = INDICATORS.create(col).compute(df)[col].to_numpy()
    ref = talib.CDLXSIDEGAP3METHODS(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    # Force the first 'lookback' bars to 0 on both sides (TA-Lib lookback warm-up).
    ref[:_LOOKBACK] = 0.0
    np.testing.assert_array_equal(our, ref)


def test_xside_gap_three_methods_parity_synthetic():
    _check(deterministic_frame())


def test_xside_gap_three_methods_parity_real():
    _check(real_frame())  # genuine AAPL daily bars (real gaps)
