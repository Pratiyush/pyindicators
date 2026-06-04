"""On-Neck parity — EXACT integer match vs ``talib.CDLONNECK`` (synthetic + real).

On-Neck is a bearish-only pattern: TA-Lib emits -100 or 0 (never the ±80 partial score). Both
the deterministic walk and the real AAPL fixture contain a genuine -100 hit, so the parity
sweep exercises a real signal, not just an all-zero column.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.on_neck import on_neck  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("on_neck").compute(df)["on_neck"].to_numpy()
    ref = talib.CDLONNECK(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_on_neck_parity_synthetic():
    df = deterministic_frame()
    ref = talib.CDLONNECK(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the synthetic walk contains a real bearish hit
    _check(df)


def test_on_neck_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLONNECK(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the real fixture contains a real bearish hit
    _check(df)
