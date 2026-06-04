"""Rising/Falling Three Methods parity — EXACT integer match vs ``talib.CDLRISEFALL3METHODS``.

Validated with no tolerance on both the synthetic deterministic frame and genuine AAPL daily
bars (candles are integer-exact). The first ``_LOOKBACK`` bars are forced to 0 to match TA-Lib.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.rise_fall_three_methods import (  # noqa: F401  (import fires @register)
    rise_fall_three_methods,
)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("rise_fall_three_methods").compute(df)[
        "rise_fall_three_methods"
    ].to_numpy()
    ref = talib.CDLRISEFALL3METHODS(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_rise_fall_three_methods_parity_synthetic():
    _check(deterministic_frame())


def test_rise_fall_three_methods_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLRISEFALL3METHODS(*_ohlc(df)).astype("float64")
    assert np.any(ref != 0)  # the real fixture actually triggers the pattern at least once
    _check(df)
