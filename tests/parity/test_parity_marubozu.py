"""Marubozu parity — EXACT integer match vs ``talib.CDLMARUBOZU`` (synthetic + real)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.marubozu import marubozu  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("marubozu").compute(df)["marubozu"].to_numpy()
    ref = talib.CDLMARUBOZU(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_marubozu_parity_synthetic():
    _check(deterministic_frame())


def test_marubozu_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
