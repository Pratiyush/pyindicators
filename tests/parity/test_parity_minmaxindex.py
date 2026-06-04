"""MINMAXINDEX parity vs TA-Lib — synthetic and real data.

MINMAXINDEX is a deterministic integer oracle (no EMA/Wilder seeding to converge), returning a
pair ``(minidx, maxidx)`` of absolute indices. Parity is therefore an *exact* equality check over
the full series for BOTH outputs, not a tail+rtol comparison. TA-Lib back-fills the first
``timeperiod-1`` bars of each output with the fill ``0`` and we reproduce that exactly, so the
whole series matches (no NaN masking needed). talib returns int32; we compare as float64 since our
contract emits float64.
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
    # No NaNs (warm-up is the fill 0), so the whole series must match exactly.
    np.testing.assert_array_equal(our, ref)


def _check(df, length):
    out = INDICATORS.create("minmaxindex", length=length).compute(df)
    minidx, maxidx = talib.MINMAXINDEX(df["close"].to_numpy(dtype="float64"), timeperiod=length)
    _exact(out["minidx"], minidx)
    _exact(out["maxidx"], maxidx)


def test_minmaxindex_parity_synthetic_default():
    _check(deterministic_frame(), 30)


def test_minmaxindex_parity_synthetic_short_window():
    # A short window exercises the rescan/tie-break path far more often than length=30.
    _check(deterministic_frame(), 5)


def test_minmaxindex_parity_synthetic_length_two():
    # length=2 is the minimal window: every bar rescans, stressing the strict-comparison tie-break.
    _check(deterministic_frame(), 2)


def test_minmaxindex_parity_real():
    _check(real_frame(), 30)


def test_minmaxindex_parity_real_short_window():
    _check(real_frame(), 14)
