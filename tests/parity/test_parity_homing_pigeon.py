"""Homing Pigeon parity — EXACT integer match vs ``talib.CDLHOMINGPIGEON`` (synthetic + real).

The pattern fires on both standard fixtures (the deterministic walk and the real AAPL daily
bars), and a hand-crafted frame that triggers the +100 signal is also checked bit-exactly to
cover the firing path directly. All comparisons are exact (no tolerance) — candles are integer
outputs (here pure 0/+100, no ±80 partial-penetration score).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.homing_pigeon import homing_pigeon  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("homing_pigeon").compute(df)["homing_pigeon"].to_numpy()
    ref = talib.CDLHOMINGPIGEON(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _trigger_frame() -> pd.DataFrame:
    # 11 black warm-up bars (body 6) then a textbook Homing Pigeon: a long black candle and a
    # short black candle whose small body sits inside it, so the +100 firing path is exercised.
    o = [100.0] * 11 + [110.0, 108.0]
    h = [100.5] * 11 + [110.5, 108.5]
    low = [93.5] * 11 + [99.5, 101.5]
    c = [94.0] * 11 + [100.0, 102.0]
    n = len(o)
    return pd.DataFrame(
        {
            "open": np.array(o),
            "high": np.array(h),
            "low": np.array(low),
            "close": np.array(c),
            "volume": np.ones(n),
        }
    )


def test_homing_pigeon_parity_synthetic():
    _check(deterministic_frame())


def test_homing_pigeon_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_homing_pigeon_parity_trigger():
    df = _trigger_frame()
    ref = talib.CDLHOMINGPIGEON(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the crafted frame actually fires the bullish signal
    _check(df)
