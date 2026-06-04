"""DPO + SWMA parity vs pandas-ta."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")

LONG = deterministic_frame()
C = LONG["close"]


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=80):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_dpo_parity():
    _p(INDICATORS.create("dpo", length=20).compute(LONG)["dpo"], pta.dpo(C, length=20, centered=False))


def test_swma_parity():
    _p(INDICATORS.create("swma", length=10).compute(LONG)["swma"], pta.swma(C, length=10))
