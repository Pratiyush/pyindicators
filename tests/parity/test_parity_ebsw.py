"""EBSW parity vs ``pandas_ta_classic.ebsw`` — synthetic and real data.

The high-pass + SuperSmoother + 3-bar wave/power pipeline reproduces the reference bit-for-bit
(observed max |Δ| == 0 on both frames), and the NaN/0.0-seed warm-up positions match exactly.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.cycle.ebsw import ebsw  # noqa: F401 — import so @register fires

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=300):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    # Warm-up NaN convention must match the reference exactly.
    assert np.array_equal(np.isnan(our), np.isnan(ref))
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df, *, length=40, bars=10, min_overlap=300):
    ref = pta.ebsw(df["close"], length=length, bars=bars)
    ours = INDICATORS.create("ebsw", length=length, bars=bars).compute(df)["ebsw"]
    _p(ours, ref, min_overlap=min_overlap)


def test_ebsw_parity_synthetic():
    _check(deterministic_frame())


def test_ebsw_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_ebsw_parity_synthetic_alt_params():
    _check(deterministic_frame(), length=48, bars=12)


def test_ebsw_parity_real_alt_params():
    _check(real_frame(), length=39, bars=5, min_overlap=300)
