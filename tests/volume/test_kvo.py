"""Klinger Volume Oscillator — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_kvo_zero_on_constant_volume():
    # constant signed volume -> fast EMA == slow EMA -> oscillator 0 after warm-up
    c = np.arange(1.0, 120.0)  # steady up-trend keeps the sign constant (+1)
    out = INDICATORS.create("kvo").compute(frame(c, high=c, low=c, volume=[1000.0] * 119))
    np.testing.assert_allclose(out["kvo"].dropna().to_numpy(), 0.0, atol=1e-6)


def test_kvo_positive_when_up_volume_expands():
    c = np.arange(1.0, 120.0)
    vol = np.linspace(100.0, 5000.0, 119)  # rising volume on up days
    out = INDICATORS.create("kvo").compute(frame(c, high=c, low=c, volume=vol))["kvo"]
    assert out.iloc[-1] > 0


def test_kvo_short_frame_all_nan():
    out = INDICATORS.create("kvo").compute(deterministic_frame(40))["kvo"]
    assert out.isna().all()  # 40 bars < slow(55) warm-up
