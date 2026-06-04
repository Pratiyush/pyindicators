"""Natural log (ln) parity vs TA-Lib ``LN`` — synthetic and real data."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-12, atol=0.0, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


# Both fixtures carry strictly-positive closes, so every bar is in-domain and TA-Lib's
# only divergence (close == 0 -> -inf, which we map to NaN) never arises here.
def test_ln_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("ln").compute(df)["ln"], talib.LN(df["close"].to_numpy()))


def test_ln_parity_real():
    df = real_frame()
    _p(INDICATORS.create("ln").compute(df)["ln"], talib.LN(df["close"].to_numpy()))
