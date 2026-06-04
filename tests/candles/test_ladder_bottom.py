"""Ladder Bottom — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.ladder_bottom import ladder_bottom  # noqa: F401  (fires @register)

# 14 warm-up bars with a 4.0 high-low range so the ShadowVeryShort average is ~0.4 by the time
# the pattern forms; the fourth black bar carries a long upper shadow that clears that average.
_WARM = 14
_WO = [100.0] * _WARM
_WC = [101.0] * _WARM
_WH = [103.0] * _WARM
_WL = [99.0] * _WARM


def _lad(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("ladder_bottom").compute(df)["ladder_bottom"].to_numpy()


def _pattern():
    # bars 14-16 (i-4,i-3,i-2): three black candles, lower opens AND lower closes.
    # bar 17 (i-1): black with a long upper shadow (high 109, body top 104).
    # bar 18 (i): white opening above the prior open (105>104) and closing above the prior
    # high (110>109) -> talib emits +100 at bar 18.
    o = _WO + [120.0, 115.0, 110.0, 104.0, 105.0]
    c = _WC + [112.0, 107.0, 102.0, 100.0, 110.0]
    h = _WH + [120.3, 115.3, 110.3, 109.0, 110.3]
    low = _WL + [111.7, 106.7, 101.7, 99.7, 104.7]
    return o, h, low, c


def test_ladder_bottom_golden_hit():
    o, h, low, c = _pattern()
    assert _lad(o, h, low, c)[18] == 100.0


def test_ladder_bottom_warmup_is_zero():
    o, h, low, c = _pattern()
    np.testing.assert_array_equal(_lad(o, h, low, c)[:14], 0.0)  # TA-Lib lookback = 14


def test_ladder_bottom_fifth_must_be_white():
    # Turn the fifth bar black (close < open) -> no pattern.
    o, h, low, c = _pattern()
    o[18], c[18] = 110.0, 105.0
    assert _lad(o, h, low, c)[18] == 0.0


def test_ladder_bottom_fifth_close_must_exceed_prior_high():
    # Fifth bar closes at the prior high (not strictly above) -> no pattern.
    o, h, low, c = _pattern()
    c[18] = 109.0  # == high[17]
    assert _lad(o, h, low, c)[18] == 0.0


def test_ladder_bottom_fifth_open_must_exceed_prior_open():
    # Fifth bar opens at the prior open (not strictly above) -> no pattern.
    o, h, low, c = _pattern()
    o[18] = 104.0  # == open[17]
    assert _lad(o, h, low, c)[18] == 0.0


def test_ladder_bottom_fourth_needs_upper_shadow():
    # Strip the fourth bar's upper shadow (high down to its body top) -> no pattern.
    o, h, low, c = _pattern()
    h[17] = 104.0  # body top, no upper shadow
    assert _lad(o, h, low, c)[18] == 0.0


def test_ladder_bottom_first_three_must_be_black():
    # Turn the first of the three black candles white -> no pattern.
    o, h, low, c = _pattern()
    o[14], c[14] = 112.0, 120.0
    assert _lad(o, h, low, c)[18] == 0.0


def test_ladder_bottom_opens_must_step_lower():
    # Break the strictly-lower-open chain (second open above the first) -> no pattern.
    o, h, low, c = _pattern()
    o[15] = 121.0
    assert _lad(o, h, low, c)[18] == 0.0


def test_ladder_bottom_short_frame_is_zero():
    # Frame shorter than the 14-bar lookback -> all zeros.
    n = 9
    o = [110.0] * n
    c = [109.0] * n
    h = [110.5] * n
    low = [108.5] * n
    out = _lad(o, h, low, c)
    assert out.shape == (n,)
    np.testing.assert_array_equal(out, 0.0)


def test_ladder_bottom_constant_frame_is_zero():
    # A constant (doji) frame has no black candles -> all zeros, never NaN.
    c = [100.0] * 40
    out = INDICATORS.create("ladder_bottom").compute(frame(c))["ladder_bottom"].to_numpy()
    np.testing.assert_array_equal(out, 0.0)


def test_ladder_bottom_output_contract():
    o, h, low, c = _pattern()
    out = INDICATORS.create("ladder_bottom").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["ladder_bottom"]
    assert set(np.unique(out["ladder_bottom"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
