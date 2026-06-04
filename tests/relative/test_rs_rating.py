"""RS Rating — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_constant_series_is_one():
    out = INDICATORS.create("rs_rating", lookbacks=(2, 3), weights=(1.0, 1.0)).compute(
        frame([5.0] * 10)
    )["rs_rating"]
    np.testing.assert_allclose(out.dropna(), 1.0)  # no change over any lookback


def test_uptrend_above_one():
    out = INDICATORS.create("rs_rating", lookbacks=(2, 3), weights=(1.0, 1.0)).compute(
        frame(np.arange(1, 20.0))
    )["rs_rating"]
    assert out.iloc[-1] > 1.0


def test_default_finite_on_long_frame():
    out = INDICATORS.create("rs_rating").compute(deterministic_frame(300))["rs_rating"]
    assert np.isfinite(out.iloc[-1])
