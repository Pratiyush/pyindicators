"""R-Squared parity vs pandas-ta — synthetic and real data.

No reference lib exposes r^2 directly, so the oracle is pandas-ta ``linreg(close, r=True)``
(the Pearson r of close vs a time ramp, == ``cti``) squared. Equivalent to the closed-form
coefficient of determination.
"""

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


def _ref_r_squared(close, length):
    return pta.linreg(close, length=length, r=True) ** 2  # Pearson r of close vs ramp, squared


def test_r_squared_parity_synthetic():
    df = deterministic_frame()
    _p(
        INDICATORS.create("r_squared", length=14).compute(df)["r_squared"],
        _ref_r_squared(df["close"], 14),
    )


def test_r_squared_parity_real():
    df = real_frame()
    _p(
        INDICATORS.create("r_squared", length=14).compute(df)["r_squared"],
        _ref_r_squared(df["close"], 14),
    )
