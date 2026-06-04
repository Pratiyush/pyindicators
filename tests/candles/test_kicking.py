"""Kicking — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.kicking import kicking  # noqa: F401  (import fires @register)

# 12 warm-up bars (body 2.0, tiny shadows) so BodyLong avg = 2.0 and ShadowVeryShort avg is
# well above the marubozu shadows by the time the pattern forms at bar 12 -> bar 13.
_WARM = 12
_WO = [100.0] * _WARM
_WC = [102.0] * _WARM
_WH = [102.1] * _WARM
_WL = [99.9] * _WARM


def _kick(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("kicking").compute(df)["kicking"].to_numpy()


def test_kicking_bullish():
    # Black marubozu (110->100) then a gapped-up white marubozu (120->130) -> +100.
    o = _WO + [110.0, 120.0]
    c = _WC + [100.0, 130.0]
    h = _WH + [110.05, 130.05]
    low = _WL + [99.95, 119.95]
    assert _kick(o, h, low, c)[13] == 100.0


def test_kicking_bearish():
    # White marubozu (120->130) then a gapped-down black marubozu (110->100) -> -100.
    o = _WO + [120.0, 110.0]
    c = _WC + [130.0, 100.0]
    h = _WH + [130.05, 110.05]
    low = _WL + [119.95, 99.95]
    assert _kick(o, h, low, c)[13] == -100.0


def test_kicking_no_gap_is_zero():
    # Opposite-colour marubozus that overlap (no gap) -> 0.
    o = _WO + [110.0, 105.0]
    c = _WC + [100.0, 115.0]
    h = _WH + [110.05, 115.05]
    low = _WL + [99.95, 104.95]  # low 104.95 < prev high 110.05 -> no gap
    assert _kick(o, h, low, c)[13] == 0.0


def test_kicking_same_colour_is_zero():
    # Both white marubozus with a gap up -> not opposite colours -> 0.
    o = _WO + [100.0, 120.0]
    c = _WC + [110.0, 130.0]
    h = _WH + [110.05, 130.05]
    low = _WL + [99.95, 119.95]
    assert _kick(o, h, low, c)[13] == 0.0


def test_kicking_long_shadow_is_zero():
    # Current bar has a long lower shadow (not a marubozu) -> 0.
    o = _WO + [110.0, 120.0]
    c = _WC + [100.0, 130.0]
    h = _WH + [110.05, 130.05]
    low = _WL + [99.95, 115.0]  # huge lower shadow on the current bar
    assert _kick(o, h, low, c)[13] == 0.0


def test_kicking_constant_frame_is_zero():
    # A flat doji frame (open == close, zero range) has no bodies -> all zero.
    c = [100.0] * 30
    out = _kick(c, c, c, c)
    np.testing.assert_array_equal(out, 0.0)


def test_kicking_short_frame_is_zero():
    # Fewer bars than the lookback -> all zero (no crash).
    o = [110.0, 120.0, 100.0]
    c = [100.0, 130.0, 90.0]
    h = [110.05, 130.05, 100.05]
    low = [99.95, 119.95, 89.95]
    np.testing.assert_array_equal(_kick(o, h, low, c), 0.0)


def test_kicking_warmup_is_zero():
    o = _WO + [110.0, 120.0]
    c = _WC + [100.0, 130.0]
    h = _WH + [110.05, 130.05]
    low = _WL + [99.95, 119.95]
    np.testing.assert_array_equal(_kick(o, h, low, c)[:11], 0.0)  # TA-Lib lookback = 11


def test_kicking_output_contract():
    o = _WO + [110.0, 120.0]
    c = _WC + [100.0, 130.0]
    h = _WH + [110.05, 130.05]
    low = _WL + [99.95, 119.95]
    out = INDICATORS.create("kicking").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["kicking"]
    assert set(np.unique(out["kicking"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
