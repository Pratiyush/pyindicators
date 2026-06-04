"""Ceil parity vs TA-Lib CEIL — synthetic and real data (exact element-wise oracle)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _p(our, ref, *, min_overlap=60):
    # CEIL is a pure pointwise transform (lookback 0): require an EXACT match on every
    # finite bar — no rtol/tail convergence is needed (no smoothing or seeding involved).
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_array_equal(our[mask], ref[mask])


def test_ceil_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("ceil").compute(df)["ceil"], talib.CEIL(df["close"].to_numpy()))


def test_ceil_parity_real():
    df = real_frame()
    _p(INDICATORS.create("ceil").compute(df)["ceil"], talib.CEIL(df["close"].to_numpy()))
