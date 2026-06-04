"""MAXINDEX parity vs TA-Lib — synthetic and real data.

MAXINDEX is a deterministic integer oracle (no EMA/Wilder seeding to converge), so parity is
an *exact* equality check over the full series, not a tail+rtol comparison. talib returns
int32; we compare as float64 since our contract emits float64. The warm-up fill (0) is part of
the contract and is included in the comparison.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _exact(our, ref):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    assert our.shape == ref.shape
    # MAXINDEX has no NaNs (warm-up is the fill 0), so the whole series must match exactly.
    np.testing.assert_array_equal(our, ref)


def test_maxindex_parity_synthetic_default():
    df = deterministic_frame()
    _exact(
        INDICATORS.create("maxindex", length=30).compute(df)["maxindex"],
        talib.MAXINDEX(df["close"].to_numpy(dtype="float64"), timeperiod=30),
    )


def test_maxindex_parity_synthetic_short_window():
    # A short window exercises the rescan/tie-break path far more often than length=30.
    df = deterministic_frame()
    _exact(
        INDICATORS.create("maxindex", length=5).compute(df)["maxindex"],
        talib.MAXINDEX(df["close"].to_numpy(dtype="float64"), timeperiod=5),
    )


def test_maxindex_parity_real():
    df = real_frame()
    _exact(
        INDICATORS.create("maxindex", length=30).compute(df)["maxindex"],
        talib.MAXINDEX(df["close"].to_numpy(dtype="float64"), timeperiod=30),
    )


def test_maxindex_parity_real_short_window():
    df = real_frame()
    _exact(
        INDICATORS.create("maxindex", length=14).compute(df)["maxindex"],
        talib.MAXINDEX(df["close"].to_numpy(dtype="float64"), timeperiod=14),
    )
