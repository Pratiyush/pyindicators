"""MININDEX parity vs TA-Lib — synthetic and real data.

TA-Lib returns an absolute *integer* index, so parity is an EXACT equality check (no
tolerance). TA-Lib back-fills the first ``timeperiod-1`` bars with ``0`` whereas we leave the
warm-up NaN, so we mask to the finite (valid) overlap before comparing.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _p(our, ref, *, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our)  # talib has no NaN (0-fills warm-up); our NaNs mark the warm-up
    assert mask.sum() >= min_overlap
    # Absolute integer indices -> compare exactly (no rtol/atol).
    np.testing.assert_array_equal(our[mask], ref[mask])


def test_minindex_parity_synthetic():
    for length in (14, 30):
        df = deterministic_frame()
        _p(
            INDICATORS.create("minindex", length=length).compute(df)["minindex"],
            talib.MININDEX(df["close"].to_numpy(), timeperiod=length),
        )


def test_minindex_parity_real():
    for length in (14, 30):
        df = real_frame()
        _p(
            INDICATORS.create("minindex", length=length).compute(df)["minindex"],
            talib.MININDEX(df["close"].to_numpy(), timeperiod=length),
        )
