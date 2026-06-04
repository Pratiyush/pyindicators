"""BRAR parity vs pandas-ta — synthetic and real data."""

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
    ref = pta.brar(df["open"], df["high"], df["low"], df["close"], length=26)
    out = INDICATORS.create("brar", length=26).compute(df)
    _p(out["ar"], ref.iloc[:, 0])
    _p(out["br"], ref.iloc[:, 1])


def test_brar_parity_synthetic():
    _check(deterministic_frame())


def test_brar_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
