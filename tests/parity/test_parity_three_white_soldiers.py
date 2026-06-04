"""Three White Soldiers parity — EXACT integer match vs ``talib.CDL3WHITESOLDIERS``.

Candle outputs are integer-exact, so this asserts equality with no tolerance on both the
synthetic deterministic frame and genuine AAPL daily bars. A dedicated bullish three-soldier
construction is also checked so the +100 branch is exercised (the fixtures rarely fire it).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.three_white_soldiers import (  # noqa: F401  (import fires @register)
    three_white_soldiers,
)

talib = pytest.importorskip("talib")

_LOOKBACK = 12


def _ohlc(df):
    return tuple(df[col].to_numpy(dtype="float64") for col in ("open", "high", "low", "close"))


def _check(df):
    series = INDICATORS.create("three_white_soldiers").compute(df)["three_white_soldiers"]
    our = np.array(series.to_numpy(), dtype="float64")  # copy: to_numpy() can be read-only
    ref = talib.CDL3WHITESOLDIERS(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    # Force the first lookback bars to 0 on both sides (TA-Lib emits 0 there by definition).
    our[:_LOOKBACK] = 0.0
    ref[:_LOOKBACK] = 0.0
    np.testing.assert_array_equal(our, ref)


def test_three_white_soldiers_parity_synthetic():
    _check(deterministic_frame())


def test_three_white_soldiers_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_three_white_soldiers_parity_constructed_hit():
    # A frame that actually fires the +100 branch, so parity covers a non-trivial output.
    warm = 12
    o = [100.0] * warm + [101.0, 103.0, 105.0]
    c = [100.5] * warm + [104.0, 106.0, 108.0]
    h = [100.6] * warm + [104.05, 106.05, 108.05]
    low = [99.9] * warm + [100.9, 102.9, 104.9]
    df = pd.DataFrame(
        {"open": o, "high": h, "low": low, "close": c, "volume": [1.0] * len(o)}
    )
    ref = talib.CDL3WHITESOLDIERS(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the construction does light up the pattern
    _check(df)
