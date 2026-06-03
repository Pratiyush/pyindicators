"""Rolling StdDev — golden + edge cases (population vs sample)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_constant_series_is_zero():
    out = INDICATORS.create("stdev", length=4).compute(frame([5.0] * 8))
    assert out["stdev"].iloc[:3].isna().all()
    np.testing.assert_allclose(out["stdev"].iloc[3:], 0.0)


def test_population_value_default():
    c = [1.0, 2.0, 3.0, 4.0]
    out = INDICATORS.create("stdev", length=4).compute(frame(c))  # ddof=0 default
    np.testing.assert_allclose(out["stdev"].iloc[3], np.std(c))


def test_sample_value_ddof1():
    c = [1.0, 2.0, 3.0, 4.0]
    out = INDICATORS.create("stdev", length=4, ddof=1).compute(frame(c))
    np.testing.assert_allclose(out["stdev"].iloc[3], np.std(c, ddof=1))
