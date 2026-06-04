"""ADD parity vs TA-Lib — synthetic and real data.

ADD is a literal element-wise sum (no EMA/Wilder seeding to converge), so parity is an *exact*
equality check on the finite overlap, not a tail+rtol comparison. NaN positions match by
construction (NaN propagates identically), so the finite mask never drops a disagreeing bar.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _exact(our, ref, *, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_array_equal(our[mask], ref[mask])


def test_add_parity_synthetic():
    df = deterministic_frame()
    _exact(
        INDICATORS.create("add").compute(df)["add"],
        talib.ADD(df["high"].to_numpy(dtype="float64"), df["low"].to_numpy(dtype="float64")),
    )


def test_add_parity_real():
    df = real_frame()
    _exact(
        INDICATORS.create("add").compute(df)["add"],
        talib.ADD(df["high"].to_numpy(dtype="float64"), df["low"].to_numpy(dtype="float64")),
    )
