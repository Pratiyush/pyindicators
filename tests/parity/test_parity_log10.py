"""log10 parity vs TA-Lib — synthetic and real data.

TA-Lib ``LOG10`` is exactly ``numpy.log10``; ours additionally maps non-positive inputs
to NaN. Both fixtures have strictly positive closes, so on the finite-masked overlap the
two agree to machine precision (no -inf/nan edge values arise here).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.math_transform.log10 import log10  # noqa: F401  (fires @register)

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=100):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_log10_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("log10").compute(df)["log10"], talib.LOG10(df["close"].to_numpy()))


def test_log10_parity_real():
    df = real_frame()
    _p(INDICATORS.create("log10").compute(df)["log10"], talib.LOG10(df["close"].to_numpy()))
