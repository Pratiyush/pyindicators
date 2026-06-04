"""Upside Gap Two Crows — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.upside_gap_two_crows import (  # noqa: F401  (import fires @register)
    upside_gap_two_crows,
)

# 12 warm-up white bars (body 100->102) so the BodyLong average is ~2.0 by the time the
# pattern can first form (third bar at index 14; TA-Lib lookback = 12).
_WARM = 12
_WO = [100.0] * _WARM
_WC = [102.0] * _WARM
_WH = [102.5] * _WARM
_WL = [99.5] * _WARM


def _ug2c(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("upside_gap_two_crows").compute(df)["upside_gap_two_crows"].to_numpy()


def _canonical():
    # 1st (idx12): long WHITE 100->110 (body 100..110).
    # 2nd (idx13): BLACK gapping up, body 113..115 (bottom 113 > 1st top 110).
    # 3rd (idx14): BLACK opens 116 (> 2nd open 115) and closes 112
    #              (< 2nd close 113, > 1st close 110) -> -100.
    o = _WO + [100.0, 115.0, 116.0]
    h = _WH + [110.5, 115.5, 116.5]
    low = _WL + [99.5, 112.5, 111.5]
    c = _WC + [110.0, 113.0, 112.0]
    return o, h, low, c


def test_upside_gap_two_crows_bearish_strict():
    assert _ug2c(*_canonical())[14] == -100.0


def test_upside_gap_two_crows_no_gap_is_zero():
    # 2nd body bottom merely touches the 1st body top (110): gap is strict -> 0.
    o = _WO + [100.0, 115.0, 116.0]
    h = _WH + [110.5, 115.5, 116.5]
    low = _WL + [99.5, 110.0, 111.5]
    c = _WC + [110.0, 110.0, 112.0]
    assert _ug2c(o, h, low, c)[14] == 0.0


def test_upside_gap_two_crows_third_not_black_is_zero():
    # Make the 3rd candle white (close above open): not a crow -> 0.
    o = _WO + [100.0, 115.0, 112.0]
    h = _WH + [110.5, 115.5, 117.0]
    low = _WL + [99.5, 112.5, 111.5]
    c = _WC + [110.0, 113.0, 116.0]
    assert _ug2c(o, h, low, c)[14] == 0.0


def test_upside_gap_two_crows_close_fills_gap_is_zero():
    # 3rd closes below the 1st close (110): the upside gap is filled -> 0.
    o = _WO + [100.0, 115.0, 116.0]
    h = _WH + [110.5, 115.5, 116.5]
    low = _WL + [99.5, 112.5, 108.5]
    c = _WC + [110.0, 113.0, 109.0]
    assert _ug2c(o, h, low, c)[14] == 0.0


def test_upside_gap_two_crows_constant_frame_is_zero():
    # A flat frame (all bars identical, zero bodies) never forms the pattern.
    flat = [100.0] * 30
    np.testing.assert_array_equal(_ug2c(flat, flat, flat, flat), 0.0)


def test_upside_gap_two_crows_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (no room for the pattern).
    o = [100.0, 110.0, 116.0, 116.0]
    h = [100.5, 110.5, 116.5, 116.5]
    low = [99.5, 99.5, 112.5, 111.5]
    c = [100.0, 110.0, 113.0, 112.0]
    np.testing.assert_array_equal(_ug2c(o, h, low, c), 0.0)


def test_upside_gap_two_crows_warmup_is_zero():
    o, h, low, c = _canonical()
    np.testing.assert_array_equal(_ug2c(o, h, low, c)[:12], 0.0)  # TA-Lib lookback = 12


def test_upside_gap_two_crows_output_contract():
    o, h, low, c = _canonical()
    out = INDICATORS.create("upside_gap_two_crows").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["upside_gap_two_crows"]
    values = set(np.unique(out["upside_gap_two_crows"].to_numpy()))
    assert values <= {-100.0, -80.0, 0.0, 80.0, 100.0}
