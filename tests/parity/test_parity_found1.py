"""Parity for the gap-analysis additions that have a clean oracle (vol_sma vs TA-Lib SMA)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")

LONG = deterministic_frame()


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=100):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_vol_sma_parity():
    _p(INDICATORS.create("vol_sma", length=20).compute(LONG)["vol_sma"],
       talib.SMA(LONG["volume"].to_numpy(), 20))
