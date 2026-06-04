"""Piercing parity — EXACT integer match vs ``talib.CDLPIERCING`` (synthetic + real).

Candles are integer-exact, so the comparison uses ``assert_array_equal`` with no tolerance on
both the deterministic random walk and the genuine AAPL daily fixture. TA-Lib's lookback (11)
is already enforced by ``piercing`` zeroing the first 11 bars, so the arrays align directly.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.piercing import piercing  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("piercing").compute(df)["piercing"].to_numpy()
    ref = talib.CDLPIERCING(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_piercing_parity_synthetic():
    _check(deterministic_frame())


def test_piercing_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLPIERCING(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the real fixture actually contains piercing patterns
    _check(df)
