"""Schaff Trend Cycle — golden + edge cases."""

from __future__ import annotations

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_stc_bounded_0_100():
    out = INDICATORS.create("stc").compute(deterministic_frame(300))
    for col in ("stc", "stc_stoch"):
        v = out[col].to_numpy()
        assert v.min() >= -1e-9 and v.max() <= 100.0 + 1e-9


def test_stc_varies_on_trend():
    out = INDICATORS.create("stc").compute(deterministic_frame(300))["stc"]
    assert out.std() > 1.0  # cycles, not stuck flat


def test_stc_columns_present():
    out = INDICATORS.create("stc").compute(deterministic_frame(120))
    assert list(out.columns) == ["stc", "stc_macd", "stc_stoch"]


def test_stc_constant_input_is_flat():
    # constant price -> MACD == 0 -> zero range (exercises the non-zero-range epsilon guard)
    out = INDICATORS.create("stc").compute(frame([50.0] * 120))
    assert (out["stc"].to_numpy() == 0.0).all()
    assert (out["stc_macd"].dropna().to_numpy() == 0.0).all()
