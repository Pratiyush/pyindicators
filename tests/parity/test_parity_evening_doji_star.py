"""Evening Doji Star parity — EXACT integer match vs ``talib.CDLEVENINGDOJISTAR``.

Candles are integer-exact (-100/0/100), so parity is asserted with no tolerance via
``np.testing.assert_array_equal`` on both the synthetic deterministic frame and the genuine
AAPL daily fixture. The real fixture actually fires the pattern (a -100), so it exercises the
hit path, not just the all-zero default.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.evening_doji_star import (
    evening_doji_star,  # noqa: F401  (fires @register)
)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("evening_doji_star").compute(df)["evening_doji_star"].to_numpy()
    ref = talib.CDLEVENINGDOJISTAR(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_evening_doji_star_parity_synthetic():
    _check(deterministic_frame())


def test_evening_doji_star_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLEVENINGDOJISTAR(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the real fixture genuinely triggers the bearish pattern
    _check(df)
