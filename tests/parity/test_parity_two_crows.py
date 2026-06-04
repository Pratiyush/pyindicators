"""Two Crows parity — EXACT integer match vs ``talib.CDL2CROWS`` (synthetic + real).

The pattern is rare and does not fire on the standard fixtures, so a hand-crafted frame that
*does* trigger the -100 signal is also checked bit-exactly to cover the firing path (not just
the all-zero case). All comparisons are exact (no tolerance) — candles are integer outputs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.two_crows import two_crows  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("two_crows").compute(df)["two_crows"].to_numpy()
    ref = talib.CDL2CROWS(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _trigger_frame() -> pd.DataFrame:
    # 12 long-white warm-up bars then a textbook Two Crows triplet (long white, gapped black,
    # contained black) so the -100 firing path is exercised against TA-Lib directly.
    o = [100.0] * 12 + [100.0, 115.0, 114.0]
    h = [102.5] * 12 + [110.5, 115.5, 114.2]
    low = [99.5] * 12 + [99.5, 111.5, 104.5]
    c = [102.0] * 12 + [110.0, 112.0, 105.0]
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


def test_two_crows_parity_synthetic():
    _check(deterministic_frame())


def test_two_crows_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_two_crows_parity_trigger():
    df = _trigger_frame()
    ref = talib.CDL2CROWS(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the crafted frame actually fires the bearish signal
    _check(df)
