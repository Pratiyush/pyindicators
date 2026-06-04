"""Rolling SUM parity vs TA-Lib ``SUM`` — synthetic and real data.

TA-Lib SUM and pandas' rolling sum agree to floating-point accumulation only, not bit-for-bit:
pandas keeps a compensated running total (add the new bar, drop the oldest) while TA-Lib
re-sums each window, so the two reorder the same additions and differ by a few ULP (observed
max ~2e-12 absolute / ~6e-16 relative over 477 bars). We pin ``rtol=1e-12`` — far below any
real divergence yet above pure rounding — rather than the exact match used for selection
reducers like MIN. (TA-Lib rejects ``timeperiod`` 1, so parity is checked at ``length`` 30,
well clear of that edge.)
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-12, atol=0.0, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_sum_parity_synthetic():
    df = deterministic_frame()
    _p(
        INDICATORS.create("sum", length=30).compute(df)["sum"],
        talib.SUM(df["close"].to_numpy(), timeperiod=30),
    )


def test_sum_parity_real():
    df = real_frame()
    _p(
        INDICATORS.create("sum", length=30).compute(df)["sum"],
        talib.SUM(df["close"].to_numpy(), timeperiod=30),
    )
