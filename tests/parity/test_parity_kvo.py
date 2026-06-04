"""Klinger Volume Oscillator parity vs pandas-ta — synthetic and real data."""

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
    ref = pta.kvo(df["high"], df["low"], df["close"], df["volume"], fast=34, slow=55, signal=13)
    out = INDICATORS.create("kvo", fast=34, slow=55, signal=13).compute(df)
    _p(out["kvo"], ref.iloc[:, 0])
    _p(out["kvo_signal"], ref.iloc[:, 1])


def test_kvo_parity_synthetic():
    _check(deterministic_frame())


def test_kvo_parity_real_data():
    _check(real_frame())  # genuine AAPL daily bars
