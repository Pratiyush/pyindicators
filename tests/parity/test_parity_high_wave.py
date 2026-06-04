"""High Wave parity — EXACT integer match vs ``talib.CDLHIGHWAVE`` (synthetic + real)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.high_wave import high_wave  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("high_wave").compute(df)["high_wave"].to_numpy()
    ref = talib.CDLHIGHWAVE(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_high_wave_parity_synthetic():
    _check(deterministic_frame())


def test_high_wave_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
