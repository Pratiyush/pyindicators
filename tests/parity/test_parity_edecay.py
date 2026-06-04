"""EDECAY parity vs pandas-ta_classic — synthetic and real data.

Parity is pinned to ``pandas_ta_classic.edecay`` (the recursive multiplicative variant,
``max(close, prev_out * exp(-1/length))``), NOT ``decay(mode="exp")`` — those are two distinct
functions in that library and the spec formula (``prev*exp(-1/length)``) is ``edecay``. See
``src/pyindicators/utils/edecay.py`` for the full divergence note.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.utils.edecay import edecay  # noqa: F401  (import fires @INDICATORS.register)

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_edecay_parity_synthetic():
    df = deterministic_frame()
    _p(
        INDICATORS.create("edecay", length=5).compute(df)["edecay"],
        pta.edecay(df["close"], length=5),
    )


def test_edecay_parity_synthetic_length_20():
    df = deterministic_frame()
    _p(
        INDICATORS.create("edecay", length=20).compute(df)["edecay"],
        pta.edecay(df["close"], length=20),
    )


def test_edecay_parity_real():
    df = real_frame()
    _p(
        INDICATORS.create("edecay", length=5).compute(df)["edecay"],
        pta.edecay(df["close"], length=5),
    )
