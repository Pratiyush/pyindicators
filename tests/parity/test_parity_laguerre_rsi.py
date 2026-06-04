"""Laguerre RSI parity vs pandas-ta ``lrsi`` — synthetic and real data.

pandas-ta reports the indicator on a 0..100 scale; our canonical Ehlers output is [0, 1], so
the oracle is ``lrsi / 100``. The L0..L3 recursion and the CU/CD ratio are identical (both seed
all four stages at ``close[0]`` and map a flat cascade to 0), so parity is exact to f64 noise
across the whole series — no warm-up to trim.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_laguerre_rsi_parity_synthetic():
    df = deterministic_frame()
    ours = INDICATORS.create("laguerre_rsi", gamma=0.5).compute(df)["laguerre_rsi"]
    _p(ours, pta.lrsi(df["close"], length=14, gamma=0.5) / 100.0)


def test_laguerre_rsi_parity_real():
    df = real_frame()
    ours = INDICATORS.create("laguerre_rsi", gamma=0.5).compute(df)["laguerre_rsi"]
    _p(ours, pta.lrsi(df["close"], length=14, gamma=0.5) / 100.0)


def test_laguerre_rsi_parity_other_gamma():
    # Re-check the recursion at a non-default coefficient (gamma drives the whole cascade).
    df = deterministic_frame()
    ours = INDICATORS.create("laguerre_rsi", gamma=0.7).compute(df)["laguerre_rsi"]
    _p(ours, pta.lrsi(df["close"], length=14, gamma=0.7) / 100.0)
