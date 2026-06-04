"""Tristar parity — EXACT integer match vs ``talib.CDLTRISTAR`` (synthetic + real).

CDLTRISTAR emits only ``{-100, 0, 100}`` (no partial-penetration score). The deterministic
frame actually fires the pattern (both signs), so parity covers live signals, not just the
all-zero path; the real AAPL fixture never forms three gapping dojis, so it stays all zeros —
still asserted bit-for-bit against TA-Lib.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.tristar import tristar  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("tristar").compute(df)["tristar"].to_numpy()
    ref = talib.CDLTRISTAR(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_tristar_parity_synthetic():
    df = deterministic_frame()
    ref = talib.CDLTRISTAR(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100) and np.any(ref == -100)  # the synthetic walk fires both signs
    _check(df)


def test_tristar_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
