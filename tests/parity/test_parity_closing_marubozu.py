"""Closing Marubozu parity — EXACT integer match vs ``talib.CDLCLOSINGMARUBOZU``.

Candles are integer-exact, so this asserts a bit-exact match (no tolerance) on both a
deterministic random walk and genuine AAPL daily bars. CDLCLOSINGMARUBOZU takes no
parameters and emits only -100/0/100 (no ±80 partial-penetration score).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.closing_marubozu import closing_marubozu  # noqa: F401 (fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("closing_marubozu").compute(df)["closing_marubozu"].to_numpy()
    ref = talib.CDLCLOSINGMARUBOZU(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_closing_marubozu_parity_synthetic():
    _check(deterministic_frame())


def test_closing_marubozu_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
