"""Long Run / Short Run / AMAT parity vs pandas-ta."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS
from pyindicators.base import ema
from pyindicators.trend.long_run import long_run
from pyindicators.trend.short_run import short_run

pta = pytest.importorskip("pandas_ta_classic")

LONG = deterministic_frame()
C = LONG["close"]
FAST, SLOW = ema(C, 8), ema(C, 21)


def _eq(our, ref):
    # 0/1 flags must match bar-for-bar wherever the reference is defined
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(ref)
    np.testing.assert_array_equal(our[mask], ref[mask])


def test_long_run_parity():
    _eq(long_run(FAST, SLOW, 2), pta.long_run(FAST, SLOW, length=2))


def test_short_run_parity():
    _eq(short_run(FAST, SLOW, 2), pta.short_run(FAST, SLOW, length=2))


def test_amat_parity():
    out = INDICATORS.create("amat", fast=8, slow=21, lookback=2).compute(LONG)
    ref = pta.amat(C, fast=8, slow=21, lookback=2, mamode="ema")
    _eq(out["amat_lr"], ref.iloc[:, 0])
    _eq(out["amat_sr"], ref.iloc[:, 1])
