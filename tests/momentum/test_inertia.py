"""Inertia — golden + edge cases."""

from __future__ import annotations

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_inertia_finite_after_warmup():
    out = INDICATORS.create("inertia").compute(deterministic_frame(200))["inertia"]
    assert out.dropna().size > 100


def test_inertia_flat_is_nan():
    out = INDICATORS.create("inertia").compute(frame([10.0] * 80))["inertia"]
    assert out.isna().all()  # flat -> RVI undefined -> inertia NaN


def test_inertia_short_frame_all_nan():
    out = INDICATORS.create("inertia").compute(frame([1.0, 2.0, 3.0]))["inertia"]
    assert out.isna().all()
