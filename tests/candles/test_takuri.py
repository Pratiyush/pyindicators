"""Takuri — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.candles.takuri import takuri  # noqa: F401  (fires @register)

# 10 warm-up bars (body 1.0, high-low 2.0 -> BodyDoji & ShadowVeryShort avg = 0.1 * 2.0 = 0.2)
# then a takuri, then three near-misses that must each stay 0.
_WARM = 10
_OPEN = [100.0] * _WARM + [100.0, 100.0, 100.0, 100.0]
_CLOSE = [101.0] * _WARM + [100.0, 101.0, 100.0, 100.1]
_HIGH = [101.5] * _WARM + [100.0, 101.0, 101.0, 100.1]
_LOW = [99.5] * _WARM + [97.0, 99.0, 99.0, 99.9]
# bar 10: o=c=h=100, low=97 -> doji body (0), no upper shadow, very long lower shadow (HIT)
# bar 11: big body 1.0 > BodyDoji avg -> not a doji
# bar 12: doji body but has an upper shadow (high 101) -> upper_shadow not < ShadowVeryShort
# bar 13: doji body (0.1) but the lower shadow (0.1) does not exceed the ShadowVeryLong
#         threshold (2 * own real body = 0.2) -> not a *very* long lower shadow


def _takuri(df):
    return INDICATORS.create("takuri").compute(df)["takuri"].to_numpy()


def test_takuri_golden_hit_and_misses():
    out = _takuri(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[10] == 100.0  # doji body, no upper shadow, very long lower shadow
    assert out[11] == 0.0  # body too big to be a doji
    assert out[12] == 0.0  # has an upper shadow
    assert out[13] == 0.0  # lower shadow not long enough for ShadowVeryLong


def test_takuri_warmup_is_zero():
    out = _takuri(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    np.testing.assert_array_equal(out[:_WARM], 0.0)  # TA-Lib lookback = 10


def test_takuri_constant_frame_is_zero():
    # A flat frame (open==high==low==close) has zero range: lower_shadow == 0 is never
    # strictly greater than the (zero) ShadowVeryLong threshold, so nothing fires.
    c = [100.0] * 30
    out = _takuri(frame(c, high=c, low=c, open_=c))
    np.testing.assert_array_equal(out, 0.0)


def test_takuri_short_frame_is_zero():
    # Fewer bars than the 10-bar lookback -> every output is 0 (averages undefined).
    c = [100.0, 100.0, 100.0]
    out = _takuri(frame(c, high=[100.0] * 3, low=[99.0] * 3, open_=[100.0] * 3))
    np.testing.assert_array_equal(out, 0.0)


def test_takuri_output_contract():
    out = INDICATORS.create("takuri").compute(deterministic_frame())
    assert list(out.columns) == ["takuri"]
    assert set(np.unique(out["takuri"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
