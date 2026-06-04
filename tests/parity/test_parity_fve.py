"""Finite Volume Element parity vs finta — synthetic and real data.

FVE is a pure rolling-window calc (no EMA/Wilder recurrence), so it matches finta to machine
epsilon over the *whole* finite overlap — no tail/convergence allowance needed.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

finta = pytest.importorskip("finta")
TA = finta.TA


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df):
    # finta default factor is 0.3; match it explicitly so the deadband lines up.
    out = INDICATORS.create("fve", length=22, factor=0.3).compute(df)["fve"]
    _p(out, TA.FVE(df, period=22))


def test_fve_parity_synthetic():
    _check(deterministic_frame())


def test_fve_parity_real_data():
    _check(real_frame())  # genuine AAPL daily bars


def test_fve_parity_alt_period():
    # A second (period, factor) point so parity isn't pinned to a single setting.
    df = deterministic_frame()
    out = INDICATORS.create("fve", length=13, factor=0.5).compute(df)["fve"]
    _p(out, TA.FVE(df, period=13, factor=0.5))
