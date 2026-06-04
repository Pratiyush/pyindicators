"""Harami parity — EXACT integer match vs ``talib.CDLHARAMI`` (synthetic + real).

Also exercises the ±80 partial-penetration score TA-Lib emits when exactly one containment
edge touches the previous body (present in the real AAPL fixture).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.harami import harami  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("harami").compute(df)["harami"].to_numpy()
    ref = talib.CDLHARAMI(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_harami_parity_synthetic():
    _check(deterministic_frame())


def test_harami_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLHARAMI(*_ohlc(df)).astype("float64")
    assert np.any(np.abs(ref) == 80)  # the real fixture hits the partial-penetration score
    _check(df)
