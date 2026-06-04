"""Tasuki Gap parity — EXACT integer match vs ``talib.CDLTASUKIGAP`` (synthetic + real).

Candles are integer-exact, so this asserts equality with no tolerance on both the synthetic
deterministic frame and genuine AAPL daily bars.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.tasuki_gap import tasuki_gap  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("tasuki_gap").compute(df)["tasuki_gap"].to_numpy()
    ref = talib.CDLTASUKIGAP(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_tasuki_gap_parity_synthetic():
    _check(deterministic_frame())


def test_tasuki_gap_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
