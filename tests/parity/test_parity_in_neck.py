"""In-Neck parity — EXACT integer match vs ``talib.CDLINNECK`` (synthetic + real).

In-Neck is a pure 0/-100 signal (no ±80 partial-penetration score). The real AAPL fixture
contains a genuine In-Neck, so the real-data check exercises the -100 output, not only zeros.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.in_neck import in_neck  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("in_neck").compute(df)["in_neck"].to_numpy()
    ref = talib.CDLINNECK(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_in_neck_parity_synthetic():
    _check(deterministic_frame())


def test_in_neck_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLINNECK(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the real fixture actually contains an In-Neck
    _check(df)
