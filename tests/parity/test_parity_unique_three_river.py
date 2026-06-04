"""Unique Three River parity — EXACT integer match vs ``talib.CDLUNIQUE3RIVER``.

Checked against the deterministic synthetic frame, the real AAPL fixture, and a hand-built
frame that genuinely triggers the (rare) pattern so the +100 firing branch is exercised, not
only the all-zero path. Candles are integer-exact, so the comparison uses no tolerance.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.unique_three_river import (
    unique_three_river,  # noqa: F401  (import fires @register)
)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("unique_three_river").compute(df)["unique_three_river"].to_numpy()
    ref = talib.CDLUNIQUE3RIVER(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _firing_frame() -> pd.DataFrame:
    # 12 small black warm-up bars, then a Unique Three River triplet:
    #   long black -> black body inside the 1st with a lower low -> short white opening above.
    o = [100.0] * 12 + [110.0, 108.0, 100.5]
    c = [99.6] * 12 + [100.0, 102.0, 100.9]
    h = [100.2] * 12 + [110.5, 108.5, 101.2]
    low = [99.4] * 12 + [99.0, 98.0, 100.2]
    return pd.DataFrame({"open": o, "high": h, "low": low, "close": c, "volume": np.ones(15)})


def test_unique_three_river_parity_synthetic():
    _check(deterministic_frame())


def test_unique_three_river_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_unique_three_river_parity_firing():
    df = _firing_frame()
    ref = talib.CDLUNIQUE3RIVER(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the hand-built frame actually triggers the pattern
    _check(df)
