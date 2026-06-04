"""Homing Pigeon — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.homing_pigeon import homing_pigeon  # noqa: F401  (import fires @register)

# 11 black warm-up bars (body 6) so BodyLong/BodyShort averages are ~6 by the time the pattern
# can first form at bar 11 -> bar 12 (TA-Lib lookback = 11).
_WARM = 11
_WO = [100.0] * _WARM
_WC = [94.0] * _WARM
_WH = [100.5] * _WARM
_WL = [93.5] * _WARM


def _hp(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("homing_pigeon").compute(df)["homing_pigeon"].to_numpy()


def _canonical():
    # 1st (idx11): long BLACK 110 -> 100 (body 10, > BodyLong avg 6).
    # 2nd (idx12): short BLACK, open 108 (< 110) and close 102 (> 100): small body inside -> 100.
    o = _WO + [110.0, 108.0]
    c = _WC + [100.0, 102.0]
    h = _WH + [110.5, 108.5]
    low = _WL + [99.5, 101.5]
    return o, h, low, c


def test_homing_pigeon_bullish_strict():
    assert _hp(*_canonical())[12] == 100.0


def test_homing_pigeon_first_white_is_zero():
    # Make the 1st candle white (close > open): not two black candles -> 0.
    o = _WO + [100.0, 108.0]
    c = _WC + [110.0, 102.0]
    h = _WH + [110.5, 108.5]
    low = _WL + [99.5, 101.5]
    assert _hp(o, h, low, c)[12] == 0.0


def test_homing_pigeon_second_white_is_zero():
    # Make the 2nd candle white (close > open): the second body must be black -> 0.
    o = _WO + [110.0, 102.0]
    c = _WC + [100.0, 108.0]
    h = _WH + [110.5, 108.5]
    low = _WL + [99.5, 101.5]
    assert _hp(o, h, low, c)[12] == 0.0


def test_homing_pigeon_second_opens_above_is_zero():
    # 2nd opens at 110 (not strictly below the 1st open 110): containment edge fails -> 0.
    o = _WO + [110.0, 110.0]
    c = _WC + [100.0, 102.0]
    h = _WH + [110.5, 110.5]
    low = _WL + [99.5, 101.5]
    assert _hp(o, h, low, c)[12] == 0.0


def test_homing_pigeon_second_closes_below_is_zero():
    # 2nd closes at 100 (not strictly above the 1st close 100): containment edge fails -> 0.
    o = _WO + [110.0, 108.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [110.5, 108.5]
    low = _WL + [99.5, 99.5]
    assert _hp(o, h, low, c)[12] == 0.0


def test_homing_pigeon_constant_frame_is_zero():
    # A flat frame (all bars identical, zero bodies) never forms the pattern.
    flat = [100.0] * 30
    np.testing.assert_array_equal(_hp(flat, flat, flat, flat), 0.0)


def test_homing_pigeon_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (no room for the pattern).
    o = [110.0, 108.0, 106.0]
    h = [110.5, 108.5, 106.5]
    low = [99.5, 101.5, 103.5]
    c = [100.0, 102.0, 104.0]
    np.testing.assert_array_equal(_hp(o, h, low, c), 0.0)


def test_homing_pigeon_warmup_is_zero():
    o, h, low, c = _canonical()
    np.testing.assert_array_equal(_hp(o, h, low, c)[:11], 0.0)  # TA-Lib lookback = 11


def test_homing_pigeon_output_contract():
    o, h, low, c = _canonical()
    out = INDICATORS.create("homing_pigeon").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["homing_pigeon"]
    assert set(np.unique(out["homing_pigeon"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
