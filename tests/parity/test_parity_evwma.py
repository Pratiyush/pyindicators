"""EVWMA parity vs finta — synthetic and real data (exact recurrence, masked past warm-up).

finta.TA.EVWMA still calls the pandas-1.x ``Series.iteritems`` (removed in pandas 2.0), so we
restore that alias to run finta's *actual* source as the oracle (not a reimplementation). Our
recurrence matches finta bar-for-bar; finta emits 0 during warm-up where we emit NaN, so the
finite-overlap mask drops the warm-up and the comparison stays exact (tight rtol/atol).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

finta = pytest.importorskip("finta")
TA = finta.TA

if not hasattr(pd.Series, "iteritems"):  # pandas>=2 removed it; finta's EVWMA still uses it
    pd.Series.iteritems = pd.Series.items  # type: ignore[attr-defined]


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    # Exact recurrence (no EMA/Wilder seeding ambiguity once seeded), so a tight tol is genuine.
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_evwma_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("evwma", period=20).compute(df)["evwma"], TA.EVWMA(df, period=20))


def test_evwma_parity_real():
    df = real_frame()
    _p(INDICATORS.create("evwma", period=20).compute(df)["evwma"], TA.EVWMA(df, period=20))


def test_evwma_parity_alt_period():
    df = deterministic_frame()
    _p(INDICATORS.create("evwma", period=10).compute(df)["evwma"], TA.EVWMA(df, period=10))
