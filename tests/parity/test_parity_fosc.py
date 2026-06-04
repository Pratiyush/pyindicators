"""Forecast Oscillator parity vs pandas-ta — synthetic and real data."""

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


def test_fosc_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("fosc", length=14).compute(df)["fosc"], pta.fosc(df["close"], length=14))


def test_fosc_parity_real():
    df = real_frame()
    _p(INDICATORS.create("fosc", length=14).compute(df)["fosc"], pta.fosc(df["close"], length=14))
