"""Doji Star parity — EXACT integer match vs ``talib.CDLDOJISTAR`` (synthetic + real).

CDLDOJISTAR emits only -100/0/100 (no partial-penetration score), so the match is bit-exact
with zero tolerance on every bar after the 11-bar lookback.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.doji_star import doji_star  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("doji_star").compute(df)["doji_star"].to_numpy()
    ref = talib.CDLDOJISTAR(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_doji_star_parity_synthetic():
    _check(deterministic_frame())


def test_doji_star_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
