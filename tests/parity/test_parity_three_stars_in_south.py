"""Three Stars In The South parity — EXACT integer match vs ``talib.CDL3STARSINSOUTH``.

Candle patterns are integer-valued (-100/0/100); parity is bit-exact with no tolerance, so this
uses ``assert_array_equal`` over the full series (TA-Lib's 12-bar lookback warm-up is also 0 in
our output, so the regions align bar-for-bar). The pattern is rare and does not occur in the
synthetic walk or the real AAPL fixture, so a crafted frame that genuinely fires +100 is also
checked against TA-Lib to exercise the hit path (still bit-exact, no tolerance).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

# import fires @register
from pyindicators.candles.three_stars_in_south import three_stars_in_south  # noqa: F401

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("three_stars_in_south").compute(df)["three_stars_in_south"].to_numpy()
    ref = talib.CDL3STARSINSOUTH(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _crafted_frame() -> pd.DataFrame:
    """A frame whose final three bars form a genuine Three Stars In The South (+100)."""
    n = 20
    o = np.full(n, 50.0)
    c = np.full(n, 50.0)
    h = np.full(n, 53.0)
    low = np.full(n, 47.0)
    # 1st: long black with long lower shadow.
    o[17], c[17], h[17], low[17] = 80.0, 50.0, 80.1, 19.0
    # 2nd: smaller black, opens into 1st range, higher low, lower shadow.
    o[18], c[18], h[18], low[18] = 65.0, 50.0, 65.1, 30.0
    # 3rd: small black marubozu engulfed by the 2nd bar.
    o[19], c[19], h[19], low[19] = 50.5, 50.0, 50.55, 49.9
    return pd.DataFrame({"open": o, "high": h, "low": low, "close": c, "volume": np.ones(n)})


def test_three_stars_in_south_parity_synthetic():
    _check(deterministic_frame())


def test_three_stars_in_south_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_three_stars_in_south_parity_crafted_hit():
    df = _crafted_frame()
    ref = talib.CDL3STARSINSOUTH(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the crafted frame actually fires the pattern
    _check(df)
