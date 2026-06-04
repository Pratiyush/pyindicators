"""Adaptive-MA parity vs pandas-ta (VIDYA / McGinley / SSF / HWMA; not in core TA-Lib)."""

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


def test_vidya_parity():
    _p(INDICATORS.create("vidya", length=14).compute(LONG)["vidya"], pta.vidya(C, length=14))


def test_mcgd_parity():
    _p(INDICATORS.create("mcgd", length=10).compute(LONG)["mcgd"], pta.mcgd(C, length=10))


def test_mcgd_parity_c_06():
    _p(INDICATORS.create("mcgd", length=10, c=0.6).compute(LONG)["mcgd"],
       pta.mcgd(C, length=10, c=0.6))


def test_ssf_two_pole_parity():
    _p(INDICATORS.create("ssf", length=10, poles=2).compute(LONG)["ssf"],
       pta.ssf(C, length=10, poles=2))


def test_ssf_three_pole_parity():
    _p(INDICATORS.create("ssf", length=10, poles=3).compute(LONG)["ssf"],
       pta.ssf(C, length=10, poles=3))


def test_hwma_parity():
    _p(INDICATORS.create("hwma").compute(LONG)["hwma"], pta.hwma(C))
