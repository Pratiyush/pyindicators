"""SMA — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.base import sma


def test_constant_series():
    out = INDICATORS.create("sma", length=5).compute(frame([7.0] * 12))
    assert out["sma"].iloc[:4].isna().all()  # warm-up = length-1
    np.testing.assert_allclose(out["sma"].iloc[4:], 7.0)


def test_linear_ramp_is_exact():
    n, p = 20, 5
    t = np.arange(n)
    a, b = 10.0, 2.0
    out = INDICATORS.create("sma", length=p).compute(frame(a + b * t))
    expected = a + b * (t - (p - 1) / 2)  # mean of a window of a linear ramp
    np.testing.assert_allclose(out["sma"].iloc[p - 1 :], expected[p - 1 :], rtol=1e-12)


def test_short_frame_is_all_nan():
    out = INDICATORS.create("sma", length=10).compute(frame([1.0, 2.0, 3.0]))
    assert out["sma"].isna().all()


def test_function_matches_class():
    f = frame(np.arange(1, 30.0))
    np.testing.assert_allclose(
        sma(f["close"], 7).to_numpy(),
        INDICATORS.create("sma", length=7).compute(f)["sma"].to_numpy(),
        equal_nan=True,
    )
