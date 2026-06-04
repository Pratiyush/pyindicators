"""Bias, PSL, ER, Slope, Elder Ray parity vs pandas-ta."""

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


def test_bias_parity():
    _p(INDICATORS.create("bias", length=26).compute(LONG)["bias"], pta.bias(C, length=26))


def test_psl_parity():
    _p(INDICATORS.create("psl", length=12).compute(LONG)["psl"], pta.psl(C, length=12))


def test_er_parity():
    _p(INDICATORS.create("er", length=10).compute(LONG)["er"], pta.er(C, length=10))


def test_slope_parity():
    _p(INDICATORS.create("slope", length=1).compute(LONG)["slope"], pta.slope(C, length=1))


def test_eri_parity():
    ref = pta.eri(LONG["high"], LONG["low"], LONG["close"], length=13)
    out = INDICATORS.create("eri", length=13).compute(LONG)
    _p(out["bull_power"], ref.iloc[:, 0])
    _p(out["bear_power"], ref.iloc[:, 1])
