"""Increasing / Decreasing / TTM Trend parity vs pandas-ta."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")

LONG = deterministic_frame()
C = LONG["close"]


def _p(our, ref, *, min_overlap=200):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_array_equal(our[mask], ref[mask])


def test_increasing_parity():
    _p(INDICATORS.create("increasing", length=1).compute(LONG)["increasing"],
       pta.increasing(C, length=1))


def test_decreasing_parity():
    _p(INDICATORS.create("decreasing", length=1).compute(LONG)["decreasing"],
       pta.decreasing(C, length=1))


def test_ttm_trend_parity():
    ref = pta.ttm_trend(LONG["high"], LONG["low"], LONG["close"], length=6)
    ref_col = ref.iloc[:, 0] if hasattr(ref, "iloc") and ref.ndim > 1 else ref
    _p(INDICATORS.create("ttm_trend", length=6).compute(LONG)["ttm_trend"], ref_col, min_overlap=100)
