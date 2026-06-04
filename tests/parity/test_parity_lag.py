"""Lag parity — synthetic and real data.

No reference library implements a bare bar-delay: ``lag`` is *defined* as
``pandas.Series.shift(length)``. There is therefore no external oracle to skip on; instead we
assert the indicator against that exact closed form (an independent ``numpy`` roll-with-NaN
oracle, NOT the indicator's own code path) on both the deterministic walk and committed real
market data, across several lengths. This is the structural/closed-form parity the spec calls
for when an indicator is golden-only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.utils.lag import lag  # noqa: F401  (fires @register)


def _shift_oracle(x: np.ndarray, length: int) -> np.ndarray:
    """Independent ``close.shift(length)``: first ``length`` entries NaN, rest are x[i-length]."""
    x = np.asarray(x, dtype="float64")
    out = np.full(x.size, np.nan)
    if length < x.size:
        out[length:] = x[: x.size - length]
    return out


def _p(our, ref, *, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    assert our.size == ref.size
    # NaN positions (warm-up) must line up exactly, and finite values must match bit-for-bit.
    np.testing.assert_array_equal(np.isnan(our), np.isnan(ref))
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_array_equal(our[mask], ref[mask])


def _check(df: pd.DataFrame, length: int) -> None:
    out = INDICATORS.create("lag", length=length).compute(df)["lag"]
    ref = _shift_oracle(df["close"].to_numpy(), length)
    _p(out, ref)


def test_lag_parity_synthetic():
    for length in (1, 2, 5, 14):
        _check(deterministic_frame(), length)


def test_lag_parity_real():
    for length in (1, 3, 10):
        _check(real_frame(), length)
