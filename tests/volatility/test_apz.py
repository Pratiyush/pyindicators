"""Adaptive Price Zone (APZ) — golden / closed-form + edge cases."""

from __future__ import annotations

import math

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.base import ema
from pyindicators.volatility.apz import apz  # noqa: F401 — import fires @register


def test_constant_range_known_bands():
    # close==10 (constant) and high-low==2 (constant) -> both double-EMAs settle on the
    # constant after warm-up, so middle=10 and half-width=mult*2=4 exactly.
    out = INDICATORS.create("apz", length=21, mult=2.0).compute(
        frame([10.0] * 30, high=[11.0] * 30, low=[9.0] * 30)
    )
    np.testing.assert_allclose(out["apz_middle"].dropna(), 10.0)
    np.testing.assert_allclose(out["apz_upper"].dropna(), 14.0)
    np.testing.assert_allclose(out["apz_lower"].dropna(), 6.0)


def test_flat_high_equals_low_collapses_band():
    # high==low -> zero range -> double-EMA range 0 -> bands collapse onto the midline.
    out = INDICATORS.create("apz", length=21).compute(
        frame([7.0] * 30, high=[7.0] * 30, low=[7.0] * 30)
    )
    np.testing.assert_allclose(out["apz_middle"].dropna(), 7.0)
    np.testing.assert_allclose(out["apz_upper"].dropna(), 7.0)
    np.testing.assert_allclose(out["apz_lower"].dropna(), 7.0)


def test_matches_explicit_double_ema_formula():
    # Closed form: middle = EMA(EMA(close, p)), band = mult * EMA(EMA(high-low, p)),
    # with p = round(sqrt(length)) = 5 at length 21.
    df = deterministic_frame(200)
    p = round(math.sqrt(21))
    assert p == 5
    mid = ema(ema(df["close"], p), p)
    band = 2.0 * ema(ema(df["high"] - df["low"], p), p)
    out = INDICATORS.create("apz", length=21, mult=2.0).compute(df)
    np.testing.assert_allclose(out["apz_middle"], mid, rtol=0, atol=1e-12, equal_nan=True)
    np.testing.assert_allclose(out["apz_upper"], mid + band, rtol=0, atol=1e-12, equal_nan=True)
    np.testing.assert_allclose(out["apz_lower"], mid - band, rtol=0, atol=1e-12, equal_nan=True)


def test_bands_symmetric_and_ordered():
    df = deterministic_frame(200)
    out = INDICATORS.create("apz").compute(df)
    # upper + lower == 2*middle (band is added/subtracted symmetrically)
    s = (out["apz_upper"] + out["apz_lower"]).dropna()
    np.testing.assert_allclose(s, 2.0 * out["apz_middle"].dropna())
    # with genuine range the band has width, so upper > middle > lower at the last bar
    last = out.iloc[-1]
    assert last["apz_upper"] > last["apz_middle"] > last["apz_lower"]


def test_mult_scales_half_width_linearly():
    df = deterministic_frame(200)
    a1 = INDICATORS.create("apz", length=21, mult=1.0).compute(df)
    a3 = INDICATORS.create("apz", length=21, mult=3.0).compute(df)
    # half-width is linear in mult, so (upper-middle) at mult=3 is 3x that at mult=1.
    hw1 = (a1["apz_upper"] - a1["apz_middle"]).dropna()
    hw3 = (a3["apz_upper"] - a3["apz_middle"]).dropna()
    np.testing.assert_allclose(hw3, 3.0 * hw1)


def test_short_frame_all_nan():
    # length 21 -> period 5 -> double EMA needs 2*5-1 = 9 valid bars; 5 bars -> all NaN.
    out = INDICATORS.create("apz", length=21).compute(frame([1.0, 2.0, 3.0, 4.0, 5.0]))
    assert out.isna().all().all()


def test_output_contract():
    out = INDICATORS.create("apz").compute(deterministic_frame(60))
    assert list(out.columns) == ["apz_middle", "apz_upper", "apz_lower"]
    assert all(str(out[c].dtype) == "float64" for c in out.columns)
    assert len(out) == 60
