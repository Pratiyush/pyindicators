"""Three Outside parity — EXACT integer match vs ``talib.CDL3OUTSIDE`` (synthetic + real).

CDL3OUTSIDE is a purely geometric three-bar pattern (no CandleSettings averaging) emitting
only -100/0/100; parity is bit-exact with no tolerance on both the deterministic walk and the
genuine AAPL daily fixture.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.three_outside import three_outside  # noqa: F401  (fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("three_outside").compute(df)["three_outside"].to_numpy()
    ref = talib.CDL3OUTSIDE(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_three_outside_parity_synthetic():
    _check(deterministic_frame())


def test_three_outside_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDL3OUTSIDE(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100) and np.any(ref == -100)  # fixture exercises both directions
    _check(df)
