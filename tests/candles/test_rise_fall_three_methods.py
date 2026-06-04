"""Rising/Falling Three Methods — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.rise_fall_three_methods import (  # noqa: F401  (import fires @register)
    rise_fall_three_methods,
)

_ALLOWED = {-100.0, -80.0, 0.0, 80.0, 100.0}


def _rf(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("rise_fall_three_methods").compute(df)[
        "rise_fall_three_methods"
    ].to_numpy()


def _warmup():
    """14 modest white bars so BodyLong/BodyShort averages are ~1.0 before the pattern."""
    o = [100.0] * 14
    h = [101.2] * 14
    low = [99.8] * 14
    c = [101.0] * 14
    return o, h, low, c


def test_rising_three_methods_is_plus_100():
    # white / black / black / black / white, the 3 small bodies falling within bar1's range,
    # 5th opens above the 4th close and closes above bar1's close -> +100 at the 5th bar.
    o, h, low, c = _warmup()
    o += [100.0, 108.0, 107.0, 106.0, 105.5]
    h += [110.5, 108.5, 107.5, 106.5, 112.5]
    low += [99.5, 106.5, 105.5, 104.5, 105.0]
    c += [110.0, 107.0, 106.0, 105.0, 112.0]
    out = _rf(o, h, low, c)
    assert out[18] == 100.0


def test_falling_three_methods_is_minus_100():
    # black / white / white / white / black, the 3 small bodies rising within bar1's range,
    # 5th opens below the 4th close and closes below bar1's close -> -100 at the 5th bar.
    o, h, low, c = _warmup()
    o += [110.0, 101.0, 102.0, 103.0, 103.5]
    h += [110.5, 102.5, 103.5, 104.5, 104.0]
    low += [99.5, 100.5, 101.5, 102.5, 97.5]
    c += [100.0, 102.0, 103.0, 104.0, 98.0]
    out = _rf(o, h, low, c)
    assert out[18] == -100.0


def test_wrong_mid_colour_is_zero():
    # A white 2nd candle (instead of black) after a rising 1st breaks the colour pattern -> 0.
    o, h, low, c = _warmup()
    o += [100.0, 107.0, 107.0, 106.0, 105.5]
    h += [110.5, 108.5, 107.5, 106.5, 112.5]
    low += [99.5, 106.5, 105.5, 104.5, 105.0]
    c += [110.0, 108.0, 106.0, 105.0, 112.0]  # bar15 closes 108 > open 107 -> white
    out = _rf(o, h, low, c)
    assert out[18] == 0.0


def test_fifth_not_beyond_first_close_is_zero():
    # 5th white closes 109 < bar1 close 110, so it fails the "close beyond the 1st" test -> 0.
    o, h, low, c = _warmup()
    o += [100.0, 108.0, 107.0, 106.0, 105.5]
    h += [110.5, 108.5, 107.5, 106.5, 109.5]
    low += [99.5, 106.5, 105.5, 104.5, 105.0]
    c += [110.0, 107.0, 106.0, 105.0, 109.0]
    out = _rf(o, h, low, c)
    assert out[18] == 0.0


def test_constant_frame_is_all_zero():
    out = _rf([100.0] * 40, [100.0] * 40, [100.0] * 40, [100.0] * 40)
    assert not out.any()


def test_short_frame_is_all_zero():
    # Fewer than (lookback + 1) bars: nothing can match, length is preserved.
    for m in (0, 1, 5, 14, 15):
        out = _rf([100.0] * m, [101.0] * m, [99.0] * m, [100.5] * m)
        assert len(out) == m
        assert not out.any()


def test_lookback_zeros_first_14():
    o, h, low, c = _warmup()
    o += [100.0, 108.0, 107.0, 106.0, 105.5]
    h += [110.5, 108.5, 107.5, 106.5, 112.5]
    low += [99.5, 106.5, 105.5, 104.5, 105.0]
    c += [110.0, 107.0, 106.0, 105.0, 112.0]
    out = _rf(o, h, low, c)
    np.testing.assert_array_equal(out[:14], 0.0)  # TA-Lib lookback = 14


def test_output_values_are_in_allowed_set():
    o, h, low, c = _warmup()
    o += [100.0, 108.0, 107.0, 106.0, 105.5]
    h += [110.5, 108.5, 107.5, 106.5, 112.5]
    low += [99.5, 106.5, 105.5, 104.5, 105.0]
    c += [110.0, 107.0, 106.0, 105.0, 112.0]
    out = _rf(o, h, low, c)
    assert set(np.unique(out)).issubset(_ALLOWED)
