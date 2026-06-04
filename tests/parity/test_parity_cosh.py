"""cosh parity vs TA-Lib COSH — synthetic and real data (element-wise, exact)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-12, atol=0.0, min_overlap=100):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    # COSH is a stateless element-wise transform == numpy.cosh, so parity is exact.
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_cosh_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("cosh").compute(df)["cosh"], talib.COSH(df["close"].to_numpy()))


def test_cosh_parity_real():
    df = real_frame()
    _p(INDICATORS.create("cosh").compute(df)["cosh"], talib.COSH(df["close"].to_numpy()))
