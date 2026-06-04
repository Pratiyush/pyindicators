"""HT_TRENDMODE parity vs TA-Lib ``HT_TRENDMODE`` — synthetic and real data.

The Hilbert recurrence reproduces TA-Lib's 0/1 regime flag exactly once past the 63-bar
lookback. Unlike the float HT_* functions, TA-Lib returns an *integer* array here, so its
warm-up region is filled with 0 rather than NaN; we therefore compare only on the region
where our output is defined (index >= 63), where the flag matches bit-for-bit.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.cycle.ht_trendmode import ht_trendmode  # import so @register fires

talib = pytest.importorskip("talib")


def _p(our, ref, *, min_overlap=300):
    our = np.asarray(our, dtype="float64")
    # TA-Lib returns int 0/1 with no NaN warm-up; cast to float so finite-overlap aligns.
    ref = np.asarray(ref, dtype="float64")
    # Our defined region is exactly where we are finite (TA-Lib is finite everywhere).
    mask = np.isfinite(our)
    assert mask.sum() >= min_overlap
    # A discrete 0/1 flag must match exactly — no tolerance.
    np.testing.assert_array_equal(our[mask], ref[mask])
    # And the values are strictly the regime flags 0/1.
    assert set(np.unique(our[mask])).issubset({0.0, 1.0})


def test_ht_trendmode_parity_synthetic():
    df = deterministic_frame()
    ours = INDICATORS.create("ht_trendmode").compute(df)["ht_trendmode"]
    _p(ours, talib.HT_TRENDMODE(df["close"].to_numpy()))


def test_ht_trendmode_parity_real():
    df = real_frame()
    ours = INDICATORS.create("ht_trendmode").compute(df)["ht_trendmode"]
    _p(ours, talib.HT_TRENDMODE(df["close"].to_numpy()))


def test_ht_trendmode_functional_matches_registry():
    df = real_frame()
    fn = ht_trendmode(df["close"])
    reg = INDICATORS.create("ht_trendmode").compute(df)["ht_trendmode"]
    np.testing.assert_array_equal(fn.to_numpy(), reg.to_numpy())
