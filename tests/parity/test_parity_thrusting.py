"""Thrusting parity — EXACT integer match vs ``talib.CDLTHRUSTING`` (synthetic + real).

Thrusting is a pure 0/-100 signal (no ±80 partial-penetration score). Both the deterministic
random-walk frame and the genuine AAPL daily fixture contain Thrusting bars, so each real-data
check exercises the -100 output, not only zeros.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.thrusting import thrusting  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("thrusting").compute(df)["thrusting"].to_numpy()
    ref = talib.CDLTHRUSTING(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_thrusting_parity_synthetic():
    df = deterministic_frame()
    ref = talib.CDLTHRUSTING(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the synthetic frame actually contains a Thrusting
    _check(df)


def test_thrusting_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLTHRUSTING(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the real fixture actually contains a Thrusting
    _check(df)
