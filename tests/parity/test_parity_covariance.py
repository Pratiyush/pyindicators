"""Covariance parity — canonical pandas closed-form oracle.

No reference TA library (talib / pandas-ta / finta / ta) exposes a direct rolling
covariance, so per the spec the oracle is pandas itself: ``high.rolling(length).cov(low)``
(sample covariance, ddof=1). pandas is a hard dependency, so there is no optional library to
``importorskip`` here — we assert exact equality against that closed-form oracle on both the
synthetic walk and the real committed market fixture.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS


def _p(our, ref, *, rtol=1e-10, atol=1e-10, min_overlap=80):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _oracle(df, length):
    return df["high"].rolling(length, min_periods=length).cov(df["low"])


def test_covariance_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("covariance", length=30).compute(df)["covariance"], _oracle(df, 30))


def test_covariance_parity_real():
    df = real_frame()
    _p(INDICATORS.create("covariance", length=30).compute(df)["covariance"], _oracle(df, 30))


def test_covariance_parity_real_short_length():
    # A second length on real data guards the warm-up boundary and ddof default.
    df = real_frame()
    _p(INDICATORS.create("covariance", length=14).compute(df)["covariance"], _oracle(df, 14))
