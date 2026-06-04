"""Separating Lines — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.separating_lines import (  # noqa: F401  (import fires @register)
    separating_lines,
)

# 11 warm-up bars (small bodies/ranges) so BodyLong/ShadowVeryShort/Equal averages are well
# defined by the time the pattern forms at bar 11 -> bar 12 (TA-Lib lookback = 11).
_WARM = 11
_WO = [100.0] * _WARM
_WC = [100.2] * _WARM
_WH = [100.4] * _WARM
_WL = [99.8] * _WARM


def _sep(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("separating_lines").compute(df)["separating_lines"].to_numpy()


def test_separating_lines_bullish():
    # Black candle (110->105) then a white belt-hold with the SAME open (110), a long body and
    # a negligible lower shadow -> bullish separating line +100.
    o = _WO + [110.0, 110.0]
    c = _WC + [105.0, 116.0]
    h = _WH + [110.3, 116.3]
    low = _WL + [104.7, 109.95]
    assert _sep(o, h, low, c)[12] == 100.0


def test_separating_lines_bearish():
    # White candle (105->110) then a black belt-hold with the SAME open (105), a long body and
    # a negligible upper shadow -> bearish separating line -100.
    o = _WO + [105.0, 105.0]
    c = _WC + [110.0, 99.0]
    h = _WH + [110.3, 105.05]
    low = _WL + [104.7, 98.7]
    assert _sep(o, h, low, c)[12] == -100.0


def test_separating_lines_same_color_is_zero():
    # Two white candles (not opposite colours) -> not a separating line -> 0.
    o = _WO + [105.0, 105.0]
    c = _WC + [110.0, 116.0]
    h = _WH + [110.3, 116.3]
    low = _WL + [104.7, 104.95]
    assert _sep(o, h, low, c)[12] == 0.0


def test_separating_lines_different_open_is_zero():
    # Opposite colours and a long belt-hold, but the opens differ well beyond the Equal
    # threshold -> not a separating line -> 0.
    o = _WO + [110.0, 113.0]
    c = _WC + [105.0, 119.0]
    h = _WH + [110.3, 119.3]
    low = _WL + [104.7, 112.95]
    assert _sep(o, h, low, c)[12] == 0.0


def test_separating_lines_belt_hold_required_is_zero():
    # Opposite colours and same open, but the current white candle has a long lower shadow
    # (not a belt-hold) -> 0.
    o = _WO + [110.0, 110.0]
    c = _WC + [105.0, 116.0]
    h = _WH + [110.3, 116.3]
    low = _WL + [104.7, 104.0]  # deep lower shadow
    assert _sep(o, h, low, c)[12] == 0.0


def test_separating_lines_warmup_is_zero():
    o = _WO + [110.0, 110.0]
    c = _WC + [105.0, 116.0]
    h = _WH + [110.3, 116.3]
    low = _WL + [104.7, 109.95]
    np.testing.assert_array_equal(_sep(o, h, low, c)[:11], 0.0)  # TA-Lib lookback = 11


def test_separating_lines_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros.
    o = [100.0, 101.0, 102.0]
    out = _sep(o, o, o, o)
    np.testing.assert_array_equal(out, 0.0)


def test_separating_lines_constant_frame_is_zero():
    # A flat constant frame has zero-length bodies everywhere -> never a long belt-hold -> 0.
    const = [100.0] * 40
    out = _sep(const, const, const, const)
    np.testing.assert_array_equal(out, 0.0)


def test_separating_lines_output_contract():
    o = _WO + [110.0, 110.0]
    c = _WC + [105.0, 116.0]
    h = _WH + [110.3, 116.3]
    low = _WL + [104.7, 109.95]
    out = INDICATORS.create("separating_lines").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["separating_lines"]
    values = set(np.unique(out["separating_lines"].to_numpy()))
    assert values <= {-100.0, -80.0, 0.0, 80.0, 100.0}
