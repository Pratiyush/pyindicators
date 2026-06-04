"""Rolling statistics — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_zscore_constant_is_nan():
    out = INDICATORS.create("zscore", length=5).compute(frame([5.0] * 12))["zscore"]
    assert out.iloc[4:].isna().all()  # stdev 0 -> guarded


def test_zscore_finite_on_trend():
    out = INDICATORS.create("zscore", length=5).compute(frame(np.arange(1, 30.0)))["zscore"]
    assert np.isfinite(out.iloc[-1])


def test_mad_constant_is_zero():
    out = INDICATORS.create("mad", length=4).compute(frame([5.0] * 10))["mad"]
    np.testing.assert_allclose(out.iloc[3:], 0.0)


def test_median_known():
    out = INDICATORS.create("median", length=3).compute(frame([1.0, 5.0, 3.0, 8.0]))["median"]
    np.testing.assert_allclose(out.iloc[2], 3.0)  # median(1,5,3)
    np.testing.assert_allclose(out.iloc[3], 5.0)  # median(5,3,8)


def test_quantile_extremes():
    f = frame([1.0, 5.0, 3.0, 8.0, 2.0])
    qmin = INDICATORS.create("quantile", length=3, q=0.0).compute(f)["quantile"]
    qmax = INDICATORS.create("quantile", length=3, q=1.0).compute(f)["quantile"]
    np.testing.assert_allclose(qmin.iloc[2], 1.0)  # min(1,5,3)
    np.testing.assert_allclose(qmax.iloc[2], 5.0)  # max(1,5,3)


def test_skew_kurtosis_finite():
    f = deterministic_frame(100)
    assert np.isfinite(INDICATORS.create("skew").compute(f)["skew"].iloc[-1])
    assert np.isfinite(INDICATORS.create("kurtosis").compute(f)["kurtosis"].iloc[-1])


def test_entropy_constant_is_log_n():
    out = INDICATORS.create("entropy", length=8, base=2.0).compute(frame([5.0] * 20))["entropy"]
    np.testing.assert_allclose(out.dropna(), np.log2(8), atol=1e-9)  # uniform p -> log2(N)
