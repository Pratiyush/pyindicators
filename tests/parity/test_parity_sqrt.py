"""Square Root parity vs TA-Lib ``SQRT`` — synthetic and real data.

SQRT is a pointwise op with no lookback, so parity is exact (rtol=0, atol=0) over the full
finite overlap. OHLCV closes are strictly positive, so the negative-domain guard never fires
here; that branch is covered in the golden tests instead.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=0.0, atol=0.0, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_sqrt_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("sqrt").compute(df)["sqrt"], talib.SQRT(df["close"].to_numpy()))


def test_sqrt_parity_real():
    df = real_frame()
    _p(INDICATORS.create("sqrt").compute(df)["sqrt"], talib.SQRT(df["close"].to_numpy()))
