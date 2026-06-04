"""Morning Star parity — EXACT integer match vs ``talib.CDLMORNINGSTAR`` (synthetic + real).

No tolerance — candles are integer-exact. The real AAPL fixture actually triggers the +100
signal, and a hand-crafted frame exercises the firing path directly; the ``penetration`` factor
is swept on real data so it threads through to TA-Lib bit-exactly.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.morning_star import morning_star  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df, **kw):
    our = INDICATORS.create("morning_star", **kw).compute(df)["morning_star"].to_numpy()
    ref = talib.CDLMORNINGSTAR(*_ohlc(df), **kw).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _trigger_frame() -> pd.DataFrame:
    # 12 long-black warm-up bars then a textbook Morning Star triplet: long black, gapped-down
    # short star, white candle closing deep into the first body — the +100 firing path.
    o = [102.0] * 12 + [110.0, 96.5, 98.0]
    h = [102.5] * 12 + [110.5, 97.0, 107.8]
    low = [99.5] * 12 + [99.5, 96.0, 97.5]
    c = [100.0] * 12 + [100.0, 96.0, 107.5]
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


def test_morning_star_parity_synthetic():
    _check(deterministic_frame())


def test_morning_star_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLMORNINGSTAR(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100)  # the real fixture actually triggers the pattern
    _check(df)


def test_morning_star_parity_trigger():
    df = _trigger_frame()
    ref = talib.CDLMORNINGSTAR(*_ohlc(df)).astype("float64")
    assert ref[14] == 100  # sanity: the crafted frame fires in TA-Lib too
    _check(df)


@pytest.mark.parametrize("penetration", [0.0, 0.1, 0.3, 0.5, 0.7, 0.9])
def test_morning_star_parity_penetration(penetration):
    # The penetration factor must thread through to TA-Lib bit-exactly on real data.
    _check(real_frame(), penetration=penetration)
    _check(_trigger_frame(), penetration=penetration)
