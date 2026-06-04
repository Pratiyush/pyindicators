"""Jurik Moving Average parity vs pandas-ta — synthetic and real data.

JMA is a deterministic scalar recursion seeded from the first close (no SMA/EMA warm-up
ambiguity), so our faithful port matches pandas-ta bit-for-bit; we still compare on the finite
tail with a tight rtol/atol for the masked overlap.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.trend.jma import jma  # noqa: F401 — import so @register fires before create

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_jma_parity_synthetic():
    df = deterministic_frame()
    _p(
        INDICATORS.create("jma", length=7, phase=0.0).compute(df)["jma"],
        pta.jma(df["close"], length=7, phase=0),
    )


def test_jma_parity_real():
    df = real_frame()
    _p(
        INDICATORS.create("jma", length=7, phase=0.0).compute(df)["jma"],
        pta.jma(df["close"], length=7, phase=0),
    )


def test_jma_parity_phase_and_length():
    # Non-default length and a non-zero phase exercise the PR coefficient and band math.
    df = deterministic_frame()
    _p(
        INDICATORS.create("jma", length=10, phase=50.0).compute(df)["jma"],
        pta.jma(df["close"], length=10, phase=50),
    )
