"""RSX parity vs pandas-ta-classic — synthetic and real data.

The port is a line-for-line copy of pandas-ta's stateful cascade, so agreement is exact;
we still mask to the finite overlap and compare the tail (the indicator is path-dependent
and shares the reference's in-place 0.0 seed at ``length-1``).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.momentum.rsx import rsx  # noqa: F401  (import fires @INDICATORS.register)

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_rsx_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("rsx", length=14).compute(df)["rsx"], pta.rsx(df["close"], length=14))


def test_rsx_parity_real():
    df = real_frame()
    _p(INDICATORS.create("rsx", length=14).compute(df)["rsx"], pta.rsx(df["close"], length=14))


@pytest.mark.parametrize("length", [7, 21])
def test_rsx_parity_real_lengths(length):
    df = real_frame()
    _p(
        INDICATORS.create("rsx", length=length).compute(df)["rsx"],
        pta.rsx(df["close"], length=length),
    )
