"""CTI (Correlation Trend Indicator) — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_cti_perfect_uptrend_is_one():
    out = INDICATORS.create("cti", length=12).compute(frame(np.arange(1.0, 40.0)))["cti"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 1.0)  # price == straight rising line


def test_cti_perfect_downtrend_is_minus_one():
    out = INDICATORS.create("cti", length=12).compute(frame(np.arange(40.0, 1.0, -1.0)))["cti"]
    np.testing.assert_allclose(out.dropna().to_numpy(), -1.0)


def test_cti_bounds():
    out = INDICATORS.create("cti", length=12).compute(deterministic_frame(200))["cti"]
    v = out.dropna().to_numpy()
    assert v.min() >= -1.0 - 1e-9 and v.max() <= 1.0 + 1e-9


def test_cti_flat_is_nan():
    out = INDICATORS.create("cti", length=12).compute(frame([5.0] * 40))["cti"]
    assert out.isna().all()  # zero price variance -> correlation undefined
