"""Belt-hold — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.belt_hold import belt_hold  # noqa: F401  (import fires @register)

# 10 warm-up bars (small body 0.4, range 2.0 so BodyLong avg = 0.4 and ShadowVeryShort = 0.2)
# then the signal bar at index 10. BodyLong is the average of the 10 PRIOR bars (exclusive of
# the current bar), so the warm-up sets both the long-body and very-short-shadow thresholds.
_WARM = 10
_W_OPEN = [100.0] * _WARM
_W_CLOSE = [100.4] * _WARM
_W_HIGH = [101.0] * _WARM
_W_LOW = [99.0] * _WARM


def _belt(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("belt_hold").compute(df)["belt_hold"].to_numpy()


def _seq(open_bar, high_bar, low_bar, close_bar):
    return (
        _W_OPEN + [open_bar],
        _W_HIGH + [high_bar],
        _W_LOW + [low_bar],
        _W_CLOSE + [close_bar],
    )


def test_belt_hold_bullish_white_no_lower_shadow():
    # White, long body (open->close = 3.0 > 0.4 avg), open == low (no lower shadow) -> +100.
    o, h, low, c = _seq(100.0, 103.5, 100.0, 103.0)
    out = _belt(o, h, low, c)
    assert out[10] == 100.0


def test_belt_hold_bearish_black_no_upper_shadow():
    # Black, long body (open->close = 3.0), open == high (no upper shadow) -> -100.
    o, h, low, c = _seq(103.0, 103.0, 99.5, 100.0)
    out = _belt(o, h, low, c)
    assert out[10] == -100.0


def test_belt_hold_white_with_lower_shadow_is_zero():
    # White, long body, but a long lower shadow (low well below the open) -> 0 (not a belt).
    o, h, low, c = _seq(100.0, 103.5, 98.0, 103.0)
    out = _belt(o, h, low, c)
    assert out[10] == 0.0


def test_belt_hold_short_body_is_zero():
    # White, no lower shadow, but the body is tiny (not a long body) -> 0.
    o, h, low, c = _seq(100.0, 100.5, 100.0, 100.1)
    out = _belt(o, h, low, c)
    assert out[10] == 0.0


def test_belt_hold_constant_frame_is_zero():
    # A flat OHLC frame (no bodies, no shadows) is never a belt-hold.
    out = _belt([100.0] * 20, [100.0] * 20, [100.0] * 20, [100.0] * 20)
    np.testing.assert_array_equal(out, 0.0)


def test_belt_hold_short_frame_is_zero():
    # Fewer bars than the lookback -> the average never fills -> all zeros.
    out = _belt([100.0, 101.0, 99.0], [101.5, 101.5, 99.5], [99.5, 100.5, 98.0],
                [101.0, 100.0, 98.5])
    np.testing.assert_array_equal(out, 0.0)


def test_belt_hold_lookback_zeros_first_ten():
    o, h, low, c = _seq(100.0, 103.5, 100.0, 103.0)
    out = _belt(o, h, low, c)
    np.testing.assert_array_equal(out[:10], 0.0)  # TA-Lib lookback = BodyLong period (10)


def test_belt_hold_output_contract():
    o, h, low, c = _seq(100.0, 103.5, 100.0, 103.0)
    out = INDICATORS.create("belt_hold").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["belt_hold"]
    assert set(np.unique(out["belt_hold"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
