"""Three Inside parity — EXACT integer match vs ``talib.CDL3INSIDE`` (synthetic + real).

CDL3INSIDE is a pure -100/0/100 signal (no ±80 partial-penetration score), so the comparison
is a bit-exact integer equality with no tolerance, on both the deterministic walk and genuine
AAPL daily bars.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.three_inside import three_inside  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("three_inside").compute(df)["three_inside"].to_numpy()
    ref = talib.CDL3INSIDE(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_three_inside_parity_synthetic():
    _check(deterministic_frame())


def test_three_inside_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDL3INSIDE(*_ohlc(df)).astype("float64")
    assert np.any(ref != 0)  # the real fixture actually exercises the pattern
    _check(df)
