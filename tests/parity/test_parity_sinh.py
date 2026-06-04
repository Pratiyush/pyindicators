"""sinh parity vs TA-Lib SINH — synthetic and real data.

SINH is a pure element-wise transform with no warm-up. On these frames close ~ 50-135, so
sinh(close) is order 1e23-1e58: absolute diffs are meaningless at that scale, so parity is
checked with a relative tolerance (rtol) and only on the finite overlap. A small-value case
(scaled close) exercises the precise near-origin regime where atol also bites.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-9, atol=1e-8, min_overlap=100):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_sinh_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("sinh").compute(df)["sinh"], talib.SINH(df["close"].to_numpy()))


def test_sinh_parity_real():
    df = real_frame()
    _p(INDICATORS.create("sinh").compute(df)["sinh"], talib.SINH(df["close"].to_numpy()))


def test_sinh_parity_small_values():
    # Scale close into a small range so sinh stays O(1): exercises the precise regime where
    # absolute tolerance matters, and confirms exact agreement with TA-Lib element-wise.
    df = deterministic_frame().copy()
    df["close"] = (df["close"] - df["close"].mean()) / 20.0
    _p(
        INDICATORS.create("sinh").compute(df)["sinh"],
        talib.SINH(df["close"].to_numpy()),
        rtol=1e-12,
        atol=1e-12,
    )
