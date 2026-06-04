"""Forecast Oscillator — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_fosc_on_perfect_line():
    # On a unit-slope line the next-bar TSF is exactly close+1, so fosc = 100*(c-(c+1))/c
    # = -100/c (the forecast leads price by one step in a steady trend).
    out = INDICATORS.create("fosc", length=14).compute(frame(np.arange(1.0, 50.0)))["fosc"]
    np.testing.assert_allclose(out.dropna().to_numpy(), -100.0 / np.arange(14.0, 50.0), atol=1e-7)


def test_fosc_finite_and_varies_on_real_trend():
    out = INDICATORS.create("fosc", length=14).compute(deterministic_frame(200))["fosc"]
    v = out.dropna().to_numpy()
    assert v.size > 100 and v.std() > 0


def test_fosc_short_frame_all_nan():
    out = INDICATORS.create("fosc", length=14).compute(frame([1.0, 2.0, 3.0]))["fosc"]
    assert out.isna().all()
