"""Parity for CFO/PGO/CG (momentum) and PVR (volume) vs pandas-ta."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")

LONG = deterministic_frame()
C = LONG["close"]


def _p(our, ref, *, rtol=1e-5, atol=1e-5, min_overlap=80):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_cfo_parity():
    _p(INDICATORS.create("cfo", length=9).compute(LONG)["cfo"], pta.cfo(C, length=9))


def test_pgo_parity_tail():
    # PGO divides by EMA(ATR); ATR's Wilder seed differs from pandas-ta early but converges,
    # so the tail matches closely.
    ref = pta.pgo(LONG["high"], LONG["low"], LONG["close"], length=14).to_numpy()[-150:]
    our = INDICATORS.create("pgo", length=14).compute(LONG)["pgo"].to_numpy()[-150:]
    _p(our, ref, rtol=1e-3, atol=1e-3, min_overlap=100)


def test_cg_parity():
    _p(INDICATORS.create("cg", length=10).compute(LONG)["cg"], pta.cg(C, length=10))


def test_pvr_parity():
    _p(INDICATORS.create("pvr").compute(LONG)["pvr"], pta.pvr(C, LONG["volume"]))
