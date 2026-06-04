"""Stalled Pattern parity — EXACT integer match vs ``talib.CDLSTALLEDPATTERN`` (synthetic + real).

CDLSTALLEDPATTERN is bearish-only (0 or -100); the real AAPL fixture exercises the -100 hits,
and a seeded synthetic frame is used to exercise a -100 hit on synthetic bars as well.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.stalled_pattern import (  # noqa: F401  (import fires @register)
    stalled_pattern,
)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("stalled_pattern").compute(df)["stalled_pattern"].to_numpy()
    ref = talib.CDLSTALLEDPATTERN(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_stalled_parity_synthetic():
    _check(deterministic_frame())


def test_stalled_parity_synthetic_seeded_hit():
    df = deterministic_frame(n=250, seed=0)  # this walk actually triggers the bearish pattern
    ref = talib.CDLSTALLEDPATTERN(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)
    _check(df)


def test_stalled_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLSTALLEDPATTERN(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the real fixture actually triggers the bearish pattern
    _check(df)
