"""Hanging Man — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.hanging_man import hanging_man  # noqa: F401  (import fires @register)

# 11 warm-up bars with a constant high-low range of 2.0 (so Near = 0.2 * 2.0 = 0.4 and
# ShadowVeryShort = 0.1 * 2.0 = 0.2) and a body of 0.4 (so BodyShort average = 0.4). The signal
# bar lands at index 11. The candle averages use the avgPeriod bars ENDING at i-1, so the
# warm-up fixes every threshold the signal bar is measured against.
_WARM = 11
_W_OPEN = [100.0] * _WARM
_W_CLOSE = [100.4] * _WARM
_W_HIGH = [101.0] * _WARM
_W_LOW = [99.0] * _WARM


def _hm(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("hanging_man").compute(df)["hanging_man"].to_numpy()


def _seq(open_bar, high_bar, low_bar, close_bar):
    return (
        _W_OPEN + [open_bar],
        _W_HIGH + [high_bar],
        _W_LOW + [low_bar],
        _W_CLOSE + [close_bar],
    )


def test_hanging_man_golden_hit():
    # Hammer shape at the top of the rising warm-up: tiny body (0.1 < 0.4), long lower shadow
    # (1.9 > 0.1 real body), no upper shadow (0.0 < 0.2), and the prior high 101.0 is within
    # Near (0.4) of the body bottom 101.5  ->  101.0 <= 101.5 + 0.4. Bearish -> -100.
    o, h, low, c = _seq(101.6, 101.6, 99.7, 101.5)
    out = _hm(o, h, low, c)
    assert out[11] == -100.0


def test_hanging_man_no_uptrend_is_zero():
    # Same hammer shape but the body sits far BELOW the prior high (prior high 101.0 is well
    # above body bottom 96.0 + Near 0.4) -> not an uptrend context -> 0.
    o, h, low, c = _seq(96.1, 96.1, 94.2, 96.0)
    out = _hm(o, h, low, c)
    assert out[11] == 0.0


def test_hanging_man_long_upper_shadow_is_zero():
    # A long upper shadow disqualifies the hammer shape even with the uptrend present -> 0.
    o, h, low, c = _seq(101.5, 103.0, 99.6, 101.6)
    out = _hm(o, h, low, c)
    assert out[11] == 0.0


def test_hanging_man_no_lower_shadow_is_zero():
    # Small body, very short upper shadow, but NO long lower shadow -> not a hanging man -> 0.
    o, h, low, c = _seq(101.5, 101.7, 101.4, 101.6)
    out = _hm(o, h, low, c)
    assert out[11] == 0.0


def test_hanging_man_big_body_is_zero():
    # A long body (not the required small body) is never a hanging man -> 0.
    o, h, low, c = _seq(101.5, 104.6, 99.6, 104.5)
    out = _hm(o, h, low, c)
    assert out[11] == 0.0


def test_hanging_man_constant_frame_is_zero():
    # A flat OHLC frame (no bodies, no shadows) is never a hanging man.
    out = _hm([100.0] * 20, [100.0] * 20, [100.0] * 20, [100.0] * 20)
    np.testing.assert_array_equal(out, 0.0)


def test_hanging_man_short_frame_is_zero():
    # Fewer bars than the lookback -> the averages never fill -> all zeros.
    out = _hm(
        [100.0, 101.0, 99.0],
        [101.5, 101.5, 99.5],
        [99.5, 100.5, 98.0],
        [101.0, 100.0, 98.5],
    )
    np.testing.assert_array_equal(out, 0.0)


def test_hanging_man_lookback_zeros_first_eleven():
    o, h, low, c = _seq(101.6, 101.6, 99.7, 101.5)
    out = _hm(o, h, low, c)
    np.testing.assert_array_equal(out[:11], 0.0)  # TA-Lib lookback = 11


def test_hanging_man_output_contract():
    o, h, low, c = _seq(101.6, 101.6, 99.7, 101.5)
    out = INDICATORS.create("hanging_man").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["hanging_man"]
    assert set(np.unique(out["hanging_man"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
