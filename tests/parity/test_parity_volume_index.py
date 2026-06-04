"""NVI / PVI / PVOL parity vs pandas-ta (WAD validated structurally — not in pandas-ta)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")

LONG = deterministic_frame()


def _p(our, ref, *, rtol=1e-5, atol=1e-4, min_overlap=80):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_nvi_parity():
    _p(INDICATORS.create("nvi").compute(LONG)["nvi"], pta.nvi(LONG["close"], LONG["volume"]))


def test_pvi_parity():
    _p(INDICATORS.create("pvi").compute(LONG)["pvi"], pta.pvi(LONG["close"], LONG["volume"]))


def test_pvol_parity():
    _p(INDICATORS.create("pvol").compute(LONG)["pvol"], pta.pvol(LONG["close"], LONG["volume"]))
