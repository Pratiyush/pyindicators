"""Statistics parity vs pandas-ta (these map onto pandas rolling ops)."""

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


def test_zscore_parity():
    _p(INDICATORS.create("zscore", length=30).compute(LONG)["zscore"], pta.zscore(C, length=30))


def test_mad_parity():
    _p(INDICATORS.create("mad", length=30).compute(LONG)["mad"], pta.mad(C, length=30))


def test_median_parity():
    _p(INDICATORS.create("median", length=30).compute(LONG)["median"], pta.median(C, length=30))


def test_skew_parity():
    _p(INDICATORS.create("skew", length=30).compute(LONG)["skew"], pta.skew(C, length=30))


def test_kurtosis_parity():
    _p(INDICATORS.create("kurtosis", length=30).compute(LONG)["kurtosis"], pta.kurtosis(C, length=30))


def test_entropy_parity():
    _p(INDICATORS.create("entropy", length=10).compute(LONG)["entropy"], pta.entropy(C, length=10))
