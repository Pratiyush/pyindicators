"""Advance Block parity — EXACT integer match vs ``talib.CDLADVANCEBLOCK`` (synthetic + real).

CDLADVANCEBLOCK is bearish-only (0 or -100); the real AAPL fixture exercises the -100 hits.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.advance_block import advance_block  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("advance_block").compute(df)["advance_block"].to_numpy()
    ref = talib.CDLADVANCEBLOCK(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_advance_block_parity_synthetic():
    _check(deterministic_frame())


def test_advance_block_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLADVANCEBLOCK(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the real fixture actually triggers the bearish pattern
    _check(df)
