"""Breakaway — golden + edge cases (deterministic; no reference library).

Breakaway is a five-candle pattern; TA-Lib's sign is the *fifth* candle's colour, so the
gap-up (white-tendency) structure scores -100 and the gap-down (black-tendency) one +100.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.breakaway import breakaway  # noqa: F401  (import fires @register)

# 10 small-body warm-up bars so BodyLong's 10-bar average is well-defined and small by bar 10.
_WARM = 10


def _brk(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("breakaway").compute(df)["breakaway"].to_numpy()


def _bullish_structure():
    """Gap-UP five-bar breakaway (1st..4th white, 5th black) -> TA-Lib emits -100 at bar 14."""
    o = [100.0] * _WARM + [100.0, 114.0, 117.0, 120.0, 124.0]
    c = [100.5] * _WARM + [112.0, 116.0, 119.0, 123.0, 113.0]
    h = [100.7] * _WARM + [112.5, 116.5, 119.5, 123.5, 124.5]
    low = [99.9] * _WARM + [99.5, 113.5, 116.5, 119.5, 112.5]
    return o, h, low, c


def _bearish_structure():
    """Gap-DOWN five-bar breakaway (1st..4th black, 5th white) -> TA-Lib emits +100 at bar 14."""
    o = [100.0] * _WARM + [112.0, 98.0, 95.0, 92.0, 88.0]
    c = [99.5] * _WARM + [100.0, 96.0, 93.0, 90.0, 99.0]
    h = [100.1] * _WARM + [112.5, 98.5, 95.5, 92.5, 99.5]
    low = [99.3] * _WARM + [99.5, 95.5, 92.5, 89.5, 87.5]
    return o, h, low, c


def test_breakaway_gap_up_structure_is_minus_100():
    # Fifth candle is black -> sign is -100 even though the structure trends up.
    o, h, low, c = _bullish_structure()
    assert _brk(o, h, low, c)[14] == -100.0


def test_breakaway_gap_down_structure_is_plus_100():
    # Fifth candle is white -> sign is +100 even though the structure trends down.
    o, h, low, c = _bearish_structure()
    assert _brk(o, h, low, c)[14] == 100.0


def test_breakaway_broken_gap_is_zero():
    # Remove the gap on the 2nd bar (open it back inside the 1st body) -> no pattern.
    o, h, low, c = _bullish_structure()
    o[11] = 105.0  # was 114.0; body now overlaps the 1st candle's body -> gap-up fails
    low[11] = 104.0
    assert _brk(o, h, low, c)[14] == 0.0


def test_breakaway_first_body_not_long_is_zero():
    # Shrink the 1st candle so its body no longer exceeds the BodyLong average -> no pattern.
    o, h, low, c = _bullish_structure()
    o[10] = 100.0
    c[10] = 100.4  # tiny body, below the warm-up average -> long_first fails
    assert _brk(o, h, low, c)[14] == 0.0


def test_breakaway_close_outside_gap_is_zero():
    # Fifth candle closes below the 1st candle's close instead of inside the gap -> no pattern.
    o, h, low, c = _bullish_structure()
    c[14] = 105.0  # below close(1st)=112 -> close_in_up fails
    low[14] = 104.0
    assert _brk(o, h, low, c)[14] == 0.0


def test_breakaway_constant_frame_is_zero():
    # A flat (doji) frame can never satisfy a long first body -> all zeros.
    flat = [100.0] * 30
    out = _brk(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_breakaway_warmup_is_zero():
    o, h, low, c = _bullish_structure()
    np.testing.assert_array_equal(_brk(o, h, low, c)[:14], 0.0)  # TA-Lib lookback = 14


def test_breakaway_short_frame_is_zero():
    # Fewer bars than the lookback -> every output is 0 (no room for the pattern).
    o, h, low, c = ([100.0, 101.0, 99.0, 100.5], [101.0, 102.0, 100.0, 101.0],
                    [99.0, 100.0, 98.0, 100.0], [100.5, 101.5, 99.5, 100.8])
    out = _brk(o, h, low, c)
    assert out.shape == (4,)
    np.testing.assert_array_equal(out, 0.0)


def test_breakaway_output_contract():
    o, h, low, c = _bullish_structure()
    out = INDICATORS.create("breakaway").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["breakaway"]
    # Breakaway is strictly -100/0/100 (no ±80 partial-penetration score).
    assert set(np.unique(out["breakaway"].to_numpy())) <= {-100.0, 0.0, 100.0}


def test_breakaway_takes_no_params():
    # Params is empty + extra='forbid' -> passing a parameter is rejected.
    import pytest

    with pytest.raises((TypeError, ValueError)):
        INDICATORS.create("breakaway", penetration=0.3)
