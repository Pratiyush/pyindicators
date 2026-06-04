"""Linear Decay parity vs pandas-ta-classic — synthetic and real data.

pandas_ta_classic.decay(mode="linear") computes max(close, close.shift(1) - 1/length, 0)
with row 0 seeded to close[0]; we match that exact (non-recursive) definition, so parity is
tight (no seed/convention divergence). Import the module directly so registration fires.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.utils import decay as decay_mod  # noqa: F401  (triggers registration)

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_decay_parity_synthetic():
    df = deterministic_frame()
    _p(
        INDICATORS.create("decay", length=5).compute(df)["decay"],
        pta.decay(df["close"], length=5, mode="linear"),
    )


def test_decay_parity_synthetic_other_length():
    df = deterministic_frame()
    _p(
        INDICATORS.create("decay", length=21).compute(df)["decay"],
        pta.decay(df["close"], length=21, mode="linear"),
    )


def test_decay_parity_real():
    df = real_frame()
    _p(
        INDICATORS.create("decay", length=5).compute(df)["decay"],
        pta.decay(df["close"], length=5, mode="linear"),
    )
