"""Spinning Top parity — EXACT integer match vs ``talib.CDLSPINNINGTOP`` (synthetic + real)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.spinning_top import spinning_top  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("spinning_top").compute(df)["spinning_top"].to_numpy()
    ref = talib.CDLSPINNINGTOP(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_spinning_top_parity_synthetic():
    _check(deterministic_frame())


def test_spinning_top_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
