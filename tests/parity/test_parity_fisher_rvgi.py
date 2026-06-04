"""Fisher Transform / RVGI parity vs pandas-ta."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")

LONG = deterministic_frame()
OPN, H, L, C = LONG["open"], LONG["high"], LONG["low"], LONG["close"]


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=80):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_fisher_parity():
    ref = pta.fisher(H, L, length=9, signal=1)
    out = INDICATORS.create("fisher", length=9, signal=1).compute(LONG)
    _p(out["fisher"], ref.iloc[:, 0])
    _p(out["fisher_signal"], ref.iloc[:, 1])


def test_rvgi_parity():
    # pandas-ta orders the frame as [histogram, rvgi, signal]
    ref = pta.rvgi(OPN, H, L, C, length=14, swma_length=4)
    out = INDICATORS.create("rvgi", length=14, swma_length=4).compute(LONG)
    _p(out["rvgi_hist"], ref.iloc[:, 0])
    _p(out["rvgi"], ref.iloc[:, 1])
    _p(out["rvgi_signal"], ref.iloc[:, 2])
