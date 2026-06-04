"""Long-Legged Doji parity — EXACT integer match vs ``talib.CDLLONGLEGGEDDOJI``.

Candle patterns are integer-exact (-100/0/100), so this asserts equality with **no tolerance**
on both the synthetic deterministic frame and the genuine AAPL daily fixture.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.long_legged_doji import long_legged_doji  # noqa: F401  (fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("long_legged_doji").compute(df)["long_legged_doji"].to_numpy()
    ref = talib.CDLLONGLEGGEDDOJI(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_long_legged_doji_parity_synthetic():
    _check(deterministic_frame())


def test_long_legged_doji_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLLONGLEGGEDDOJI(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the real fixture actually fires the pattern
    _check(df)
