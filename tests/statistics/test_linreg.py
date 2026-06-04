"""Linear-regression family — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_linreg_on_perfect_line():
    # y = 2x + 10 -> regression recovers it exactly
    n = 20
    y = 10.0 + 2.0 * np.arange(n)
    f = frame(y)
    slope = INDICATORS.create("linreg_slope", length=5).compute(f)["linreg_slope"]
    np.testing.assert_allclose(slope.dropna(), 2.0, atol=1e-9)
    # LINEARREG value at current bar == the line's value there (i.e. y itself)
    lr = INDICATORS.create("linreg", length=5).compute(f)["linreg"]
    np.testing.assert_allclose(lr.iloc[4:], y[4:], atol=1e-9)
    # intercept at window start = y[t-4]
    inter = INDICATORS.create("linreg_intercept", length=5).compute(f)["linreg_intercept"]
    np.testing.assert_allclose(inter.iloc[4:], y[: n - 4], atol=1e-9)
    # TSF projects one ahead = y[t] + 2
    tsf = INDICATORS.create("tsf", length=5).compute(f)["tsf"]
    np.testing.assert_allclose(tsf.iloc[4:], y[4:] + 2.0, atol=1e-9)


def test_linreg_angle_of_known_slope():
    f = frame(10.0 + 1.0 * np.arange(20.0))  # slope 1 -> 45 degrees
    ang = INDICATORS.create("linreg_angle", length=5).compute(f)["linreg_angle"]
    np.testing.assert_allclose(ang.dropna(), 45.0, atol=1e-9)


def test_flat_series_slope_zero():
    slope = INDICATORS.create("linreg_slope", length=5).compute(frame([5.0] * 12))["linreg_slope"]
    np.testing.assert_allclose(slope.iloc[4:], 0.0, atol=1e-9)
