"""Belt-hold parity — EXACT integer match vs ``talib.CDLBELTHOLD`` (synthetic + real).

CDLBELTHOLD emits only -100/0/100 (no ±80 partial-penetration score: both shadow tests are
strict inequalities against an average, so a body edge never merely ties). Candles are
integer-exact, so this asserts equality with no tolerance on both the deterministic frame and
genuine AAPL daily bars.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.belt_hold import belt_hold  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("belt_hold").compute(df)["belt_hold"].to_numpy()
    ref = talib.CDLBELTHOLD(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_belt_hold_parity_synthetic():
    _check(deterministic_frame())


def test_belt_hold_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLBELTHOLD(*_ohlc(df)).astype("float64")
    assert np.any(ref != 0)  # the real fixture actually fires the pattern
    assert set(np.unique(ref)) <= {-100.0, 0.0, 100.0}  # no ±80 score for this pattern
    _check(df)
