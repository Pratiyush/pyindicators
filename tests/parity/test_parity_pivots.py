"""Pivot Points parity — finta ``PIVOT`` + closed-form oracle, synthetic and real data.

Pivots are a pure closed-form combination of the prior bar's H/L/C (no smoothing, no
seeding), so parity is *exact* (tight rtol/atol), not a tail/convergence check. finta is
the named reference: its ``PIVOT`` uses ``ohlc.shift()`` and the identical floor-trader
formula, so its P/S1/S2/S3/R1/R2/R3 columns must match ours bar-for-bar. We additionally
pin against an independent closed-form oracle so the test stands even if finta is absent.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

finta = pytest.importorskip("finta")
TA = finta.TA


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=80):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


# finta column -> our output column (finta also emits s4/r4, which classic pivots omit).
_MAP = {"pivot": "pivot", "s1": "s1", "s2": "s2", "s3": "s3", "r1": "r1", "r2": "r2", "r3": "r3"}


def _closed_form(df):
    """Independent reimplementation of the floor-trader formula from prior-bar H/L/C."""
    h, low_, c = df["high"].shift(1), df["low"].shift(1), df["close"].shift(1)
    p = (h + low_ + c) / 3.0
    rng = h - low_
    return {
        "pivot": p,
        "r1": 2.0 * p - low_,
        "s1": 2.0 * p - h,
        "r2": p + rng,
        "s2": p - rng,
        "r3": h + 2.0 * (p - low_),
        "s3": low_ - 2.0 * (h - p),
    }


def _check(df):
    out = INDICATORS.create("pivots").compute(df)
    ref = TA.PIVOT(df)
    for fcol, ocol in _MAP.items():
        _p(out[ocol], ref[fcol])
    # And exact agreement with our own closed-form oracle (no library dependency).
    oracle = _closed_form(df)
    for col, series in oracle.items():
        _p(out[col], series, rtol=0.0, atol=1e-12)


def test_pivots_parity_synthetic():
    _check(deterministic_frame())


def test_pivots_parity_real():
    _check(real_frame())
