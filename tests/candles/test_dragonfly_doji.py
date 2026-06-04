"""Dragonfly Doji — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.candles.dragonfly_doji import dragonfly_doji  # noqa: F401  (fires @register)

# 10 warm-up bars (body 1.0, high-low 2.0 -> BodyDoji & ShadowVeryShort avg = 0.1 * 2.0 = 0.2)
# then a dragonfly, then three near-misses that must each stay 0.
_WARM = 10
_OPEN = [100.0] * _WARM + [100.0, 100.0, 100.0, 100.0]
_CLOSE = [101.0] * _WARM + [100.0, 101.0, 100.0, 100.0]
_HIGH = [101.5] * _WARM + [100.0, 101.0, 101.0, 101.0]
_LOW = [99.5] * _WARM + [99.0, 99.0, 99.0, 100.0]
# bar 10: open=close=high=100, low=99 -> tiny body, long lower shadow, no upper shadow (HIT)
# bar 11: big body 1.0 > BodyDoji avg -> not a doji
# bar 12: doji body but has an upper shadow (high 101) -> upper_shadow not < threshold
# bar 13: doji body but no lower shadow (low 100) -> lower_shadow not > threshold


def _dragonfly(df):
    return INDICATORS.create("dragonfly_doji").compute(df)["dragonfly_doji"].to_numpy()


def test_dragonfly_golden_hit_and_misses():
    out = _dragonfly(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[10] == 100.0  # doji body, long lower shadow, no upper shadow
    assert out[11] == 0.0  # body too big to be a doji
    assert out[12] == 0.0  # has an upper shadow
    assert out[13] == 0.0  # has no lower shadow


def test_dragonfly_warmup_is_zero():
    out = _dragonfly(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    np.testing.assert_array_equal(out[:_WARM], 0.0)  # TA-Lib lookback = 10


def test_dragonfly_constant_frame_is_zero():
    # A flat frame (open==high==low==close) has zero range: lower_shadow == 0 is never
    # strictly greater than the (zero) ShadowVeryShort threshold, so nothing fires.
    c = [100.0] * 30
    out = _dragonfly(frame(c, high=c, low=c, open_=c))
    np.testing.assert_array_equal(out, 0.0)


def test_dragonfly_short_frame_is_zero():
    # Fewer bars than the 10-bar lookback -> every output is 0 (averages undefined).
    c = [100.0, 100.0, 100.0]
    out = _dragonfly(frame(c, high=[100.0] * 3, low=[99.0] * 3, open_=[100.0] * 3))
    np.testing.assert_array_equal(out, 0.0)


def test_dragonfly_output_contract():
    out = INDICATORS.create("dragonfly_doji").compute(deterministic_frame())
    assert list(out.columns) == ["dragonfly_doji"]
    assert set(np.unique(out["dragonfly_doji"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
