"""Shooting Star — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.shooting_star import shooting_star  # noqa: F401  (fires @register)

# 11 warm-up bars (body 1.0, high-low 2.0) -> BodyShort avg = 1.0, ShadowVeryShort avg = 0.2.
# Bar 11 is a normal "prior" bar whose real body spans [100, 101] (max(o,c) = 101).
# Bar 12 is a shooting star that gaps UP above it: tiny body near the low of the bar, long upper
#   shadow, no lower shadow, with min(o,c) = 110.00 > 101. -> fires (-100).
# Bar 13 has the same shape but NO gap (body back down at ~100), so the gap-up clause fails -> 0.
_WARM = 11
_OPEN = [100.0] * _WARM + [100.0, 110.10, 100.10]
_CLOSE = [101.0] * _WARM + [101.0, 110.00, 100.00]
_HIGH = [101.5] * _WARM + [101.5, 112.00, 102.00]
_LOW = [99.5] * _WARM + [99.5, 110.00, 100.00]


def _ss(df):
    return INDICATORS.create("shooting_star").compute(df)["shooting_star"].to_numpy()


def test_shooting_star_golden_hit_and_miss():
    out = _ss(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[12] == -100.0  # tiny body, long upper shadow, no lower shadow, gaps up over prior
    assert out[13] == 0.0  # identical shape but no gap-up -> not a shooting star


def test_shooting_star_warmup_is_zero():
    out = _ss(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    np.testing.assert_array_equal(out[:11], 0.0)  # TA-Lib lookback = 11 (BodyShort 10 + 1 prior)


def test_shooting_star_constant_frame_is_zero():
    # A flat frame (open == high == low == close) has no body and no shadows -> never fires.
    c = [50.0] * 40
    out = _ss(frame(c, high=c, low=c, open_=c))
    np.testing.assert_array_equal(out, 0.0)


def test_shooting_star_short_frame_is_zero():
    # Fewer bars than the lookback -> every bar is inside the warm-up -> all zeros.
    c = [100.0, 101.0, 99.0, 102.0, 98.0]
    out = _ss(frame(c, high=[x + 1 for x in c], low=[x - 1 for x in c], open_=c))
    np.testing.assert_array_equal(out, 0.0)


def test_shooting_star_output_contract():
    out = INDICATORS.create("shooting_star").compute(
        frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN)
    )
    assert list(out.columns) == ["shooting_star"]
    assert set(np.unique(out["shooting_star"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
