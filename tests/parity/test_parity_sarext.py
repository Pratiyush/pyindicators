"""Extended Parabolic SAR (SAREXT) parity vs TA-Lib — synthetic and real data.

The recursion is reverse-engineered to match ``talib.SAREXT`` *exactly* (the seed and the
post-reversal acceleration step are reproduced bit-for-bit), so parity holds over the whole
finite overlap rather than only the tail; a small rtol absorbs float64 rounding.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.trend.sarext import sarext  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-7, atol=1e-7, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _ref(df):
    return talib.SAREXT(df["high"].to_numpy(), df["low"].to_numpy())


def test_sarext_parity_talib_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("sarext").compute(df)["sarext"], _ref(df))


def test_sarext_parity_talib_real():
    df = real_frame()  # genuine AAPL daily bars (real gaps / reversals)
    _p(INDICATORS.create("sarext").compute(df)["sarext"], _ref(df))
