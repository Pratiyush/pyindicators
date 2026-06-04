"""Inertia parity vs pandas-ta — synthetic and real data."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df):
    ref = pta.inertia(df["close"], length=20, rvi_length=14)
    out = INDICATORS.create("inertia", length=20, rvi_length=14).compute(df)["inertia"]
    _p(out, ref)


def test_inertia_parity_synthetic():
    _check(deterministic_frame())


def test_inertia_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
