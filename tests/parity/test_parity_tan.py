"""TAN parity vs TA-Lib — synthetic and real data (TA-Lib TAN == np.tan, exact)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_tan_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("tan").compute(df)["tan"], talib.TAN(df["close"].to_numpy()))


def test_tan_parity_real():
    df = real_frame()
    _p(INDICATORS.create("tan").compute(df)["tan"], talib.TAN(df["close"].to_numpy()))
