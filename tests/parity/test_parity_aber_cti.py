"""Aberration / CTI parity vs pandas-ta — synthetic and real data."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-6, atol=1e-6, tail=None, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    if tail is not None:
        our, ref = our[-tail:], ref[-tail:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check_aberration(df):
    # The bands carry an ATR, whose Wilder seed converges with pandas-ta on the tail.
    ref = pta.aberration(df["high"], df["low"], df["close"], length=5, atr_length=15)
    out = INDICATORS.create("aberration", length=5, atr_length=15).compute(df)
    _p(out["aber_zg"], ref.iloc[:, 0])  # SMA midline matches full series
    for ours, col in zip(("aber_sg", "aber_xg", "aber_atr"), (1, 2, 3), strict=True):
        _p(out[ours], ref.iloc[:, col], tail=200, rtol=1e-3)


def test_aberration_parity_synthetic():
    _check_aberration(deterministic_frame())


def test_aberration_parity_real():
    _check_aberration(real_frame())


def test_cti_parity_synthetic():
    _p(INDICATORS.create("cti", length=12).compute(deterministic_frame())["cti"],
       pta.cti(deterministic_frame()["close"], length=12))


def test_cti_parity_real():
    df = real_frame()
    _p(INDICATORS.create("cti", length=12).compute(df)["cti"], pta.cti(df["close"], length=12))
