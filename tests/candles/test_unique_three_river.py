"""Unique Three River — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.unique_three_river import (
    unique_three_river,  # noqa: F401  (import fires @register)
)

# 12 black warm-up bars (body 100->94) so the BodyLong/BodyShort averages are ~6 by the time
# the pattern can first form (third bar at index 14; TA-Lib lookback = 12).
_WARM = 12
_WO = [100.0] * _WARM
_WC = [94.0] * _WARM
_WH = [100.5] * _WARM
_WL = [93.5] * _WARM


def _u3r(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("unique_three_river").compute(df)["unique_three_river"].to_numpy()


def _canonical():
    # 1st (idx12): long BLACK 110 -> 100 (body 10, > BodyLong avg ~6).
    # 2nd (idx13): BLACK, open 108 (<= 110), close 102 (> 100) -> body inside the 1st,
    #              low 98 (< 1st low 99) -> a new low (the "river").
    # 3rd (idx14): short WHITE, open 100.5 (> 2nd low 98), close 100.9 (small body) -> +100.
    o = _WO + [110.0, 108.0, 100.5]
    c = _WC + [100.0, 102.0, 100.9]
    h = _WH + [110.5, 108.5, 101.2]
    low = _WL + [99.0, 98.0, 100.2]
    return o, h, low, c


def test_unique_three_river_bullish():
    assert _u3r(*_canonical())[14] == 100.0


def test_unique_three_river_open2_tie_passes():
    # 2nd opens exactly at the 1st open (110): the top containment edge uses ``<=``, so a tie
    # still qualifies -> +100.
    o = _WO + [110.0, 110.0, 100.5]
    c = _WC + [100.0, 102.0, 100.9]
    h = _WH + [110.5, 110.5, 101.2]
    low = _WL + [99.0, 98.0, 100.2]
    assert _u3r(o, h, low, c)[14] == 100.0


def test_unique_three_river_first_white_is_zero():
    # Make the 1st candle white (close > open): the first body must be long black -> 0.
    o = _WO + [100.0, 108.0, 100.5]
    c = _WC + [110.0, 102.0, 100.9]
    h = _WH + [110.5, 108.5, 101.2]
    low = _WL + [99.0, 98.0, 100.2]
    assert _u3r(o, h, low, c)[14] == 0.0


def test_unique_three_river_no_new_low_is_zero():
    # 2nd low ties the 1st low (99): the river edge is strict (``low2 < low1``) -> 0.
    o = _WO + [110.0, 108.0, 100.5]
    c = _WC + [100.0, 102.0, 100.9]
    h = _WH + [110.5, 108.5, 101.2]
    low = _WL + [99.0, 99.0, 100.2]
    assert _u3r(o, h, low, c)[14] == 0.0


def test_unique_three_river_close2_outside_is_zero():
    # 2nd closes at 100 (not strictly above the 1st close 100): body not inside -> 0.
    o = _WO + [110.0, 108.0, 100.5]
    c = _WC + [100.0, 100.0, 100.9]
    h = _WH + [110.5, 108.5, 101.2]
    low = _WL + [99.0, 98.0, 100.2]
    assert _u3r(o, h, low, c)[14] == 0.0


def test_unique_three_river_open3_ties_low2_is_zero():
    # 3rd opens exactly at the 2nd low (98): the edge is strict (``open3 > low2``) -> 0.
    o = _WO + [110.0, 108.0, 98.0]
    c = _WC + [100.0, 102.0, 98.4]
    h = _WH + [110.5, 108.5, 98.7]
    low = _WL + [99.0, 98.0, 97.8]
    assert _u3r(o, h, low, c)[14] == 0.0


def test_unique_three_river_third_black_is_zero():
    # Make the 3rd candle black (close < open): the third body must be white -> 0.
    o = _WO + [110.0, 108.0, 100.9]
    c = _WC + [100.0, 102.0, 100.5]
    h = _WH + [110.5, 108.5, 101.2]
    low = _WL + [99.0, 98.0, 100.2]
    assert _u3r(o, h, low, c)[14] == 0.0


def test_unique_three_river_constant_frame_is_zero():
    # A flat frame (all bars identical, zero bodies) never forms the pattern.
    flat = [100.0] * 30
    np.testing.assert_array_equal(_u3r(flat, flat, flat, flat), 0.0)


def test_unique_three_river_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (no room for the pattern).
    o = [110.0, 108.0, 100.5]
    h = [110.5, 108.5, 101.2]
    low = [99.0, 98.0, 100.2]
    c = [100.0, 102.0, 100.9]
    np.testing.assert_array_equal(_u3r(o, h, low, c), 0.0)


def test_unique_three_river_warmup_is_zero():
    o, h, low, c = _canonical()
    np.testing.assert_array_equal(_u3r(o, h, low, c)[:12], 0.0)  # TA-Lib lookback = 12


def test_unique_three_river_output_contract():
    o, h, low, c = _canonical()
    out = INDICATORS.create("unique_three_river").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["unique_three_river"]
    vals = set(np.unique(out["unique_three_river"].to_numpy()))
    assert vals <= {-100.0, -80.0, 0.0, 80.0, 100.0}
