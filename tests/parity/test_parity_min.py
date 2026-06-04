"""Rolling MIN parity vs TA-Lib ``MIN`` — synthetic and real data.

TA-Lib MIN is an exact rolling reducer, so parity is exact (no smoothing/seed drift): same
NaN warm-up and bit-for-bit equal finite values over the overlap.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=0.0, atol=0.0, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_min_parity_synthetic():
    df = deterministic_frame()
    _p(
        INDICATORS.create("min", length=30).compute(df)["min"],
        talib.MIN(df["close"].to_numpy(), timeperiod=30),
    )


def test_min_parity_real():
    df = real_frame()
    _p(
        INDICATORS.create("min", length=30).compute(df)["min"],
        talib.MIN(df["close"].to_numpy(), timeperiod=30),
    )
