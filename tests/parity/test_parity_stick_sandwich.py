"""Stick Sandwich parity — EXACT integer match vs ``talib.CDLSTICKSANDWICH`` (synthetic + real).

Candles are integer-exact, so this asserts equality with no tolerance via
``np.testing.assert_array_equal``. The deterministic frame happens to contain a genuine stick
sandwich (a non-zero signal), so parity is exercised on a real fire, not just on all-zeros.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.stick_sandwich import (
    stick_sandwich,  # noqa: F401  (import fires @register)
)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("stick_sandwich").compute(df)["stick_sandwich"].to_numpy()
    ref = talib.CDLSTICKSANDWICH(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_stick_sandwich_parity_synthetic():
    df = deterministic_frame()
    ref = talib.CDLSTICKSANDWICH(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the deterministic frame contains a genuine stick sandwich
    _check(df)


def test_stick_sandwich_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
