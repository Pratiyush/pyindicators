"""Gator Oscillator parity — synthetic and real data.

No reference library ships the Gator (or the Alligator) directly, so there is no drop-in
oracle. Instead we build the Gator from ``pandas_ta_classic.rma`` — which is the *same*
SMA-seeded Wilder smoothing (TA-Lib convention) that our ``base.rma`` implements — and apply
the explicit spec formula ``upper = |jaw - teeth|`` / ``lower = -|teeth - lips|`` to those
externally-computed lines. That makes this a genuine cross-library check of both the SMMA
smoother and the Gator composition, not a self-referential one.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")


def _oracle(df, jaw=13, teeth=8, lips=5):
    med = (df["high"] + df["low"]) / 2.0
    j = pta.rma(med, length=jaw)
    t = pta.rma(med, length=teeth)
    lp = pta.rma(med, length=lips)
    return (j - t).abs(), -(t - lp).abs()


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_gator_parity_synthetic():
    df = deterministic_frame()
    out = INDICATORS.create("gator").compute(df)
    up, lo = _oracle(df)
    _p(out["gator_upper"], up)
    _p(out["gator_lower"], lo)


def test_gator_parity_real():
    df = real_frame()
    out = INDICATORS.create("gator").compute(df)
    up, lo = _oracle(df)
    _p(out["gator_upper"], up)
    _p(out["gator_lower"], lo)
