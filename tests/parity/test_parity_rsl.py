"""Relative Strength Levy parity — synthetic and real data.

No reference library ships RSL (Relative Strength Levy) directly, so the oracle is its
closed-form definition built from pandas-ta-classic's own SMA: ``close / pta.sma(close, n)``.
Both sides are exact rolling means with the same NaN warm-up, so parity is exact (rtol 0).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.momentum.rsl import rsl  # noqa: F401  (import fires @register)

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-12, atol=1e-12, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _ref(df, length=26):
    # Closed-form oracle: close / SMA(close, length), with pandas-ta supplying the SMA.
    return df["close"] / pta.sma(df["close"], length=length)


def test_rsl_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("rsl", length=26).compute(df)["rsl"], _ref(df, 26))


def test_rsl_parity_real():
    df = real_frame()
    _p(INDICATORS.create("rsl", length=26).compute(df)["rsl"], _ref(df, 26))
