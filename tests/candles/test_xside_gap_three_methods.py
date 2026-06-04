"""Upside/Downside gap three methods — golden + edge cases (deterministic; no reference lib)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.candles.xside_gap_three_methods import (  # noqa: F401  (import fires @register)
    xside_gap_three_methods,
)

# Two warm-up bars (TA-Lib lookback = 2), then the three pattern bars at indices 2, 3, 4.
_WO = [50.0, 50.0]
_WC = [50.0, 50.0]
_WH = [50.1, 50.1]
_WL = [49.9, 49.9]


def _xs(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    col = "xside_gap_three_methods"
    return INDICATORS.create(col).compute(df)[col].to_numpy()


def test_xside_gap_three_methods_upside_gap_is_100():
    # 1st & 2nd white, gap up (2nd body wholly above 1st); 3rd is black, opens inside the 2nd
    # body and closes inside the 1st body (filling the gap) -> +100 at the 3rd candle (bar 4).
    o = _WO + [40.0, 50.0, 53.0]  # 3rd opens at 53 (inside 2nd body 50..55)
    c = _WC + [42.0, 55.0, 41.0]  # 3rd closes at 41 (inside 1st body 40..42)
    h = _WH + [42.1, 55.1, 53.1]
    low = _WL + [39.9, 49.9, 40.9]
    out = _xs(o, h, low, c)
    assert out[4] == 100.0


def test_xside_gap_three_methods_downside_gap_is_minus_100():
    # 1st & 2nd black, gap down (2nd body wholly below 1st); 3rd is white, opens inside the 2nd
    # body and closes inside the 1st body -> -100 at the 3rd candle (bar 4).
    o = _WO + [60.0, 50.0, 47.0]  # 1st black: open 60 close 58 (body 58..60)
    c = _WC + [58.0, 45.0, 59.0]  # 2nd black: open 50 close 45 (body 45..50, below 1st)
    h = _WH + [60.1, 50.1, 59.1]  # 3rd white: open 47 (inside 45..50), close 59 (inside 58..60)
    low = _WL + [57.9, 44.9, 46.9]
    out = _xs(o, h, low, c)
    assert out[4] == -100.0


def test_xside_gap_three_methods_no_gap_is_zero():
    # Same shape as the upside case but the 2nd body overlaps the 1st (no gap) -> 0.
    o = _WO + [40.0, 41.0, 42.0]
    c = _WC + [42.0, 43.0, 41.5]
    h = _WH + [42.1, 43.1, 42.1]
    low = _WL + [39.9, 40.9, 40.9]
    out = _xs(o, h, low, c)
    assert out[4] == 0.0


def test_xside_gap_three_methods_third_same_color_is_zero():
    # Upside gap but the 3rd candle is white (same colour as 1st/2nd) -> not the pattern -> 0.
    o = _WO + [40.0, 50.0, 51.0]
    c = _WC + [42.0, 55.0, 53.0]  # 3rd white (close > open)
    h = _WH + [42.1, 55.1, 53.1]
    low = _WL + [39.9, 49.9, 50.9]
    out = _xs(o, h, low, c)
    assert out[4] == 0.0


def test_xside_gap_three_methods_third_closes_outside_first_is_zero():
    # Upside gap, 3rd black opens inside 2nd body but closes BELOW the 1st body -> 0.
    o = _WO + [40.0, 50.0, 53.0]
    c = _WC + [42.0, 55.0, 39.0]  # closes at 39, below the 1st body low (40)
    h = _WH + [42.1, 55.1, 53.1]
    low = _WL + [39.9, 49.9, 38.9]
    out = _xs(o, h, low, c)
    assert out[4] == 0.0


def test_xside_gap_three_methods_constant_frame_is_zero():
    # A perfectly flat frame has no bodies, no colour, no gaps -> all zeros.
    out = _xs([50.0] * 30, [50.0] * 30, [50.0] * 30, [50.0] * 30)
    np.testing.assert_array_equal(out, 0.0)


def test_xside_gap_three_methods_short_frame_is_zero():
    # Fewer bars than the lookback (2) -> everything is 0.
    o = [50.0, 51.0]
    out = _xs(o, [x + 0.1 for x in o], [x - 0.1 for x in o], o)
    np.testing.assert_array_equal(out, 0.0)


def test_xside_gap_three_methods_warmup_is_zero():
    o = _WO + [40.0, 50.0, 53.0]
    c = _WC + [42.0, 55.0, 41.0]
    h = _WH + [42.1, 55.1, 53.1]
    low = _WL + [39.9, 49.9, 40.9]
    np.testing.assert_array_equal(_xs(o, h, low, c)[:2], 0.0)  # TA-Lib lookback = 2


def test_xside_gap_three_methods_output_contract():
    df = deterministic_frame()
    out = INDICATORS.create("xside_gap_three_methods").compute(df)
    assert list(out.columns) == ["xside_gap_three_methods"]
    uniq = set(np.unique(out["xside_gap_three_methods"].to_numpy()))
    assert uniq <= {-100.0, -80.0, 0.0, 80.0, 100.0}
