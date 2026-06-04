"""Hurst Exponent — golden + edge cases."""

from __future__ import annotations

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_random_walk_in_sane_range():
    out = INDICATORS.create("hurst_exponent", length=100).compute(deterministic_frame(300))
    vals = out["hurst_exponent"].dropna().to_numpy()
    assert vals.size > 0
    assert ((vals > 0.2) & (vals < 0.9)).all()  # R/S estimate stays in a sane band


def test_flat_window_is_nan():
    out = INDICATORS.create("hurst_exponent", length=20).compute(frame([5.0] * 60))
    assert out["hurst_exponent"].isna().all()  # zero variance -> undefined
