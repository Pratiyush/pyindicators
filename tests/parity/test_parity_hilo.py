"""Gann HiLo Activator parity vs pandas-ta(_classic) — synthetic and real data.

HILO is a stateful flip line over SMA bands; both libraries use the identical SMA mamode and
the same prior-bar cross rule, so parity is *exact* (no EMA/Wilder seeding drift) on every
column — the line and both legs — once masked to the finite overlap.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")

# pandas-ta columns are HILO_<h>_<l>, HILOl_<h>_<l>, HILOs_<h>_<l> in this order.
_OURS = ("hilo", "hilo_long", "hilo_short")


def _assert_col(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=20):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    # NaN masks must line up too (stateful warm-up / leg assignment is identical).
    np.testing.assert_array_equal(np.isfinite(our), np.isfinite(ref))
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df, high_length=13, low_length=21):
    out = INDICATORS.create("hilo", high_length=high_length, low_length=low_length).compute(df)
    ref = pta.hilo(
        df["high"], df["low"], df["close"], high_length=high_length, low_length=low_length
    )
    for ours, refcol in zip(_OURS, ref.columns, strict=True):
        _assert_col(out[ours], ref[refcol])


def test_hilo_parity_synthetic():
    _check(deterministic_frame())


def test_hilo_parity_real():
    _check(real_frame())


def test_hilo_parity_nondefault_lengths():
    # A different/short pair exercises the warm-up boundary and more frequent flips.
    _check(deterministic_frame(), high_length=5, low_length=8)
