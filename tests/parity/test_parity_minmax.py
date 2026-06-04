"""MINMAX parity vs TA-Lib — synthetic and real data.

TA-Lib MINMAX is an exact rolling reducer (no EMA/Wilder seeding to converge), so parity is
*exact*: identical NaN warm-up and bit-for-bit equal finite values over the overlap, for both
the ``min`` and the ``max`` output. ``talib.MINMAX`` returns a ``(min, max)`` tuple.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _p(our, ref, *, min_overlap=60):
    # Exact rolling reducer: zero tolerance over the finite overlap.
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_array_equal(our[mask], ref[mask])


def _check(df, length):
    out = INDICATORS.create("minmax", length=length).compute(df)
    ref_min, ref_max = talib.MINMAX(df["close"].to_numpy(dtype="float64"), timeperiod=length)
    _p(out["min"], ref_min)
    _p(out["max"], ref_max)


def test_minmax_parity_synthetic_default():
    _check(deterministic_frame(), 30)


def test_minmax_parity_synthetic_short_window():
    # A short window exercises the rolling boundary far more often than length=30.
    _check(deterministic_frame(), 5)


def test_minmax_parity_real():
    _check(real_frame(), 30)


def test_minmax_parity_real_short_window():
    _check(real_frame(), 14)
