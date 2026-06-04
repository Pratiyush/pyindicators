"""Long-Legged Doji — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.long_legged_doji import long_legged_doji  # noqa: F401  (fires @register)

# 10 warm-up bars wide enough that the BodyDoji average (10% of the average high-low range,
# here 0.1 * 1.5 = 0.15) is well defined by the time the pattern forms at bar 10.
_WARM = 10
_WO = [100.0] * _WARM
_WC = [100.5] * _WARM
_WH = [101.0] * _WARM
_WL = [99.5] * _WARM


def _lld(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("long_legged_doji").compute(df)["long_legged_doji"].to_numpy()


def test_long_legged_doji_long_lower_shadow_hit():
    # Doji body (open == close) with a long lower shadow -> +100 (one long leg suffices).
    o = _WO + [100.0]
    c = _WC + [100.0]
    h = _WH + [100.5]
    low = _WL + [97.0]
    assert _lld(o, h, low, c)[10] == 100.0


def test_long_legged_doji_long_upper_shadow_hit():
    # Doji body with a long upper shadow -> +100.
    o = _WO + [100.0]
    c = _WC + [100.0]
    h = _WH + [103.0]
    low = _WL + [99.5]
    assert _lld(o, h, low, c)[10] == 100.0


def test_long_legged_doji_both_shadows_hit():
    # Doji body with long upper AND lower shadows (the classic long-legged doji) -> +100.
    o = _WO + [100.0]
    c = _WC + [100.0]
    h = _WH + [103.0]
    low = _WL + [97.0]
    assert _lld(o, h, low, c)[10] == 100.0


def test_long_legged_doji_no_shadow_is_zero():
    # A doji body that fills the whole range (no shadows at all) is not long-legged -> 0.
    o = _WO + [100.0]
    c = _WC + [100.0]
    h = _WH + [100.0]
    low = _WL + [100.0]
    assert _lld(o, h, low, c)[10] == 0.0


def test_long_legged_doji_big_body_is_not_doji():
    # A real body (0.6) larger than the BodyDoji threshold (~0.15) is not a doji even with
    # long shadows -> 0.
    o = _WO + [100.0]
    c = _WC + [100.6]
    h = _WH + [102.0]
    low = _WL + [98.0]
    assert _lld(o, h, low, c)[10] == 0.0


def test_long_legged_doji_constant_frame_is_zero():
    # A flat frame (range 0 everywhere) has no shadows -> never long-legged.
    flat = [50.0] * 30
    out = _lld(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_long_legged_doji_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (the BodyDoji average is undefined).
    o = [100.0, 100.0, 100.0]
    c = [100.0, 100.0, 100.0]
    h = [101.0, 101.0, 101.5]
    low = [99.0, 99.0, 97.0]
    np.testing.assert_array_equal(_lld(o, h, low, c), 0.0)


def test_long_legged_doji_warmup_is_zero():
    o = _WO + [100.0]
    c = _WC + [100.0]
    h = _WH + [103.0]
    low = _WL + [97.0]
    np.testing.assert_array_equal(_lld(o, h, low, c)[:10], 0.0)  # TA-Lib lookback = 10


def test_long_legged_doji_output_contract():
    o = _WO + [100.0]
    c = _WC + [100.0]
    h = _WH + [103.0]
    low = _WL + [97.0]
    out = INDICATORS.create("long_legged_doji").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["long_legged_doji"]
    vals = set(np.unique(out["long_legged_doji"].to_numpy()))
    assert vals <= {-100.0, -80.0, 0.0, 80.0, 100.0}
