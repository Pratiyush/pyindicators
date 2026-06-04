"""VAMA parity vs finta — synthetic and real data (closed-form double-rolling, no seeding)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

finta = pytest.importorskip("finta")
TA = finta.TA


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    # Closed-form (no EMA/Wilder seeding), so a tight tolerance is exact, not papered-over.
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_vama_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("vama", period=8).compute(df)["vama"], TA.VAMA(df, period=8))


def test_vama_parity_real():
    df = real_frame()
    _p(INDICATORS.create("vama", period=8).compute(df)["vama"], TA.VAMA(df, period=8))


def test_vama_parity_alt_period():
    df = deterministic_frame()
    _p(INDICATORS.create("vama", period=20).compute(df)["vama"], TA.VAMA(df, period=20))
