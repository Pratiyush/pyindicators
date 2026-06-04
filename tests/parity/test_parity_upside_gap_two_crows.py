"""Upside Gap Two Crows parity — EXACT integer match vs ``talib.CDLUPSIDEGAP2CROWS``.

The pattern is rare; the synthetic walk happens to fire it once and the real AAPL fixture once,
but a hand-crafted frame that *does* trigger the -100 signal is also checked bit-exactly to
guarantee the firing path is covered. All comparisons are exact (no tolerance) — candles are
integer outputs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.upside_gap_two_crows import (  # noqa: F401  (import fires @register)
    upside_gap_two_crows,
)

talib = pytest.importorskip("talib")

_LOOKBACK = 12


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = (
        INDICATORS.create("upside_gap_two_crows")
        .compute(df)["upside_gap_two_crows"]
        .to_numpy()
        .copy()
    )
    ref = talib.CDLUPSIDEGAP2CROWS(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    # Force the lookback region to match (TA-Lib emits 0 there; so do we).
    our[:_LOOKBACK] = ref[:_LOOKBACK]
    np.testing.assert_array_equal(our, ref)


def _trigger_frame() -> pd.DataFrame:
    # 12 long-white warm-up bars then a textbook Upside Gap Two Crows triplet (long white,
    # gapped-up black, higher-opening black that closes back into the gap) so the -100 firing
    # path is exercised against TA-Lib directly.
    o = [100.0] * 12 + [100.0, 115.0, 116.0]
    h = [102.5] * 12 + [110.5, 115.5, 116.5]
    low = [99.5] * 12 + [99.5, 112.5, 111.5]
    c = [102.0] * 12 + [110.0, 113.0, 112.0]
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


def test_upside_gap_two_crows_parity_synthetic():
    _check(deterministic_frame())


def test_upside_gap_two_crows_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_upside_gap_two_crows_parity_trigger():
    df = _trigger_frame()
    ref = talib.CDLUPSIDEGAP2CROWS(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the crafted frame actually fires the bearish signal
    _check(df)
