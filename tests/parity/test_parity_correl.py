"""CORREL parity vs TA-Lib ``CORREL`` — synthetic and real data.

Rolling Pearson r of high & low. TA-Lib and our pandas implementation agree to ~1e-12 on
genuine OHLCV; they diverge ONLY on zero-variance windows (TA-Lib -> 0.0, we keep NaN), which
do not occur in either parity frame, so no masking beyond finite-overlap is needed.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=80):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_correl_parity_synthetic():
    df = deterministic_frame()
    ours = INDICATORS.create("correl", length=30).compute(df)["correl"]
    ref = talib.CORREL(df["high"].to_numpy(), df["low"].to_numpy(), timeperiod=30)
    _p(ours, ref)


def test_correl_parity_real():
    df = real_frame()
    ours = INDICATORS.create("correl", length=30).compute(df)["correl"]
    ref = talib.CORREL(df["high"].to_numpy(), df["low"].to_numpy(), timeperiod=30)
    _p(ours, ref)
