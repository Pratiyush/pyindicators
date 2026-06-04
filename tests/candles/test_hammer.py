"""Hammer — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.hammer import hammer  # noqa: F401  (import fires @register)

# 11 warm-up bars (body 1.0, high-low 2.0) so the BodyShort/ShadowVeryShort/Near averages are
# defined by the time the pattern is evaluated at bar 12. The prior bar (11) sits low so the
# hammer body forms "near" its low.
_WARM = 11
_WO = [100.0] * _WARM
_WC = [101.0] * _WARM
_WH = [101.5] * _WARM
_WL = [99.5] * _WARM


def _ham(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("hammer").compute(df)["hammer"].to_numpy()


def test_hammer_golden_hit():
    # Bar 11: small body (99.6->99.9) near the prior bar's low (99.5), long lower shadow down
    # to 96, no upper shadow (high == body top) -> +100.
    o = _WO + [99.6]
    c = _WC + [99.9]
    h = _WH + [99.9]
    low = _WL + [96.0]
    assert _ham(o, h, low, c)[11] == 100.0


def test_hammer_long_upper_shadow_is_zero():
    # Same small body + long lower shadow but now a long upper shadow -> not a hammer.
    o = _WO + [99.6]
    c = _WC + [99.9]
    h = _WH + [103.0]  # tall upper wick disqualifies it
    low = _WL + [96.0]
    assert _ham(o, h, low, c)[11] == 0.0


def test_hammer_no_lower_shadow_is_zero():
    # Small body, negligible upper shadow, but no long lower shadow -> not a hammer.
    o = _WO + [99.6]
    c = _WC + [99.9]
    h = _WH + [99.9]
    low = _WL + [99.55]  # lower shadow too short
    assert _ham(o, h, low, c)[11] == 0.0


def test_hammer_constant_frame_is_zero():
    # A flat doji-like series (open == high == low == close) has no body/shadows -> all 0.
    c = [100.0] * 30
    out = _ham(c, c, c, c)
    np.testing.assert_array_equal(out, 0.0)


def test_hammer_warmup_is_zero():
    o = _WO + [99.6]
    c = _WC + [99.9]
    h = _WH + [99.9]
    low = _WL + [96.0]
    np.testing.assert_array_equal(_ham(o, h, low, c)[:11], 0.0)  # TA-Lib lookback = 11


def test_hammer_short_frame_is_zero():
    # Fewer bars than the lookback -> every output is 0.
    o = [100.0, 99.6, 99.6]
    c = [101.0, 99.9, 99.9]
    h = [101.5, 99.9, 99.9]
    low = [99.5, 96.0, 96.0]
    np.testing.assert_array_equal(_ham(o, h, low, c), 0.0)


def test_hammer_output_contract():
    o = _WO + [99.6]
    c = _WC + [99.9]
    h = _WH + [99.9]
    low = _WL + [96.0]
    out = INDICATORS.create("hammer").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["hammer"]
    assert set(np.unique(out["hammer"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
