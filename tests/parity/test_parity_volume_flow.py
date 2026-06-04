"""Force Index / Ease of Movement / PVT parity vs pandas-ta (not in core TA-Lib)."""

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


def test_efi_parity():
    ref = pta.efi(LONG["close"], LONG["volume"], length=13)
    _p(INDICATORS.create("efi", length=13).compute(LONG)["efi"], ref)


def test_eom_parity():
    ref = pta.eom(LONG["high"], LONG["low"], LONG["close"], LONG["volume"], length=14)
    _p(INDICATORS.create("eom", length=14).compute(LONG)["eom"], ref)


def test_pvt_parity():
    # Same values; pandas-ta scales PVT by 100 (ROC-in-percent). Ours uses the StockCharts
    # fraction convention, so we divide pandas-ta's output by 100 to compare.
    ref = pta.pvt(LONG["close"], LONG["volume"]) / 100.0
    _p(INDICATORS.create("pvt").compute(LONG)["pvt"], ref)
