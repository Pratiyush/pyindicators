"""Long Line parity — EXACT integer match vs ``talib.CDLLONGLINE`` (synthetic + real).

``CDLLONGLINE`` emits only -100/0/100 (no partial ±80 score). Parity is checked with no
tolerance on both the deterministic walk and the genuine AAPL daily fixture.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.long_line import long_line  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("long_line").compute(df)["long_line"].to_numpy()
    ref = talib.CDLLONGLINE(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_long_line_parity_synthetic():
    _check(deterministic_frame())


def test_long_line_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLLONGLINE(*_ohlc(df)).astype("float64")
    assert np.any(ref != 0)  # the real fixture actually fires the pattern
    _check(df)
