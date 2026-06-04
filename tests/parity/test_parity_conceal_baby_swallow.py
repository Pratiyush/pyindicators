"""Concealing Baby Swallow parity — EXACT integer match vs ``talib.CDLCONCEALBABYSWALL``.

Candles are integer-exact, so parity is asserted with ``np.testing.assert_array_equal`` (no
tolerance) on the deterministic synthetic frame and on genuine AAPL daily bars. The pattern is
extremely rare (it does not occur in either fixture), so a third hand-built case exercises an
actual +100 hit to prove the parity covers a firing pattern, not only the all-zero path.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.conceal_baby_swallow import (  # noqa: F401  (import fires @register)
    conceal_baby_swallow,
)

talib = pytest.importorskip("talib")

# TA-Lib lookback for CDLCONCEALBABYSWALL; force these leading bars to 0 to mirror talib exactly.
_LOOKBACK = 13


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("conceal_baby_swallow").compute(df)["conceal_baby_swallow"].to_numpy()
    ref = talib.CDLCONCEALBABYSWALL(*_ohlc(df)).astype("float64")
    ref[:_LOOKBACK] = 0.0  # talib already zeros the lookback; make the contract explicit
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _pattern_frame() -> pd.DataFrame:
    # 13 short black warm-up bars + a hand-built Concealing Baby Swallow on bars 13..16.
    warm = 13
    o = [50.0] * warm + [48.0, 43.5, 39.0, 41.5]
    c = [49.5] * warm + [44.0, 40.0, 37.5, 36.0]
    h = [50.1] * warm + [48.02, 43.52, 41.0, 41.5]
    low = [49.4] * warm + [43.98, 39.98, 37.4, 37.0]
    return pd.DataFrame({"open": o, "high": h, "low": low, "close": c, "volume": [1.0] * 17})


def test_conceal_baby_swallow_parity_synthetic():
    _check(deterministic_frame())


def test_conceal_baby_swallow_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_conceal_baby_swallow_parity_handbuilt_hit():
    df = _pattern_frame()
    ref = talib.CDLCONCEALBABYSWALL(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the hand-built frame actually fires the pattern
    _check(df)
