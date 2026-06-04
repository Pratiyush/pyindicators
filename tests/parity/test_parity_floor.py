"""FLOOR parity vs TA-Lib — synthetic and real data.

``FLOOR`` is an exact element-wise transform, so parity is bit-for-bit: assert equality on
the finite overlap (atol 0), not a tolerance band.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.math_transform.floor import floor  # noqa: F401  (fires @register)

talib = pytest.importorskip("talib")


def _p_exact(our, ref, *, min_overlap=100):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    # Exact transform: TA-Lib FLOOR == numpy.floor element-wise, so demand atol 0.
    np.testing.assert_array_equal(our[mask], ref[mask])


def test_floor_parity_synthetic():
    df = deterministic_frame()
    _p_exact(INDICATORS.create("floor").compute(df)["floor"], talib.FLOOR(df["close"].to_numpy()))


def test_floor_parity_real():
    df = real_frame()
    _p_exact(INDICATORS.create("floor").compute(df)["floor"], talib.FLOOR(df["close"].to_numpy()))
