"""Mat Hold — golden + edge cases (deterministic; no reference library).

The geometries here are cross-checked against ``talib.CDLMATHOLD`` in the parity test; this
file pins the behaviour without importing talib so it runs in the plain ``dev`` environment.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.mat_hold import mat_hold  # noqa: F401  (fires @register)

# 14 warm-up bars with a moderate body (5.0) so the shared BodyLong/BodyShort average (both
# RealBody/10/1.0) settles near 5: the long bodies (10) clear it and the small reaction bodies
# (~1) stay under it by the time the five-bar pattern forms at bars 14..18 (lookback = 14).
_WARM = 14
_WO = [100.0] * _WARM
_WC = [105.0] * _WARM
_WH = [105.2] * _WARM
_WL = [99.8] * _WARM

# A canonical bullish Mat Hold (firing bar = index 18):
#   #1 long white 100->110; #2 small black gapping above #1's body; #3, #4 small candles that
#   drift down holding shallowly within #1's body; #5 long white closing above the reaction.
_BULL_O = [100.0, 113.0, 111.0, 110.0, 109.0]
_BULL_C = [110.0, 112.0, 109.0, 108.0, 115.0]
_BULL_H = [110.2, 113.5, 111.2, 110.2, 115.2]
_BULL_L = [99.8, 111.5, 108.8, 107.8, 108.8]


def _mh(o, h, low, c, **params):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("mat_hold", **params).compute(df)["mat_hold"].to_numpy()


def test_mat_hold_bullish_is_plus_100():
    out = _mh(_WO + _BULL_O, _WH + _BULL_H, _WL + _BULL_L, _WC + _BULL_C)
    assert out[18] == 100.0


def test_mat_hold_no_gap_is_zero():
    # #2 no longer gaps above #1's body (its body sits on #1's close) -> not a Mat Hold.
    o = list(_BULL_O)
    c = list(_BULL_C)
    o[1], c[1] = 109.0, 110.0  # min(open,close)[#2] = 109 is not > max(open,close)[#1] = 110
    assert _mh(_WO + o, _WH + _BULL_H, _WL + _BULL_L, _WC + c)[18] == 0.0


def test_mat_hold_fifth_not_above_reaction_is_zero():
    # The 5th candle fails to close above the highest reaction high (113.5) -> no signal.
    c = list(_BULL_C)
    c[4] = 113.0  # close 113 < max reaction high 113.5
    assert _mh(_WO + _BULL_O, _WH + _BULL_H, _WL + _BULL_L, _WC + c)[18] == 0.0


def test_mat_hold_penetration_param():
    # Reaction candles dip to a body-low of ~106. With penetration 0.5 the floor is
    # 110 - 10*0.5 = 105 (held -> +100); with 0.3 the floor rises to 107 (breached -> 0).
    o = [100.0, 113.0, 107.0, 106.8, 108.0]
    c = [110.0, 112.5, 106.0, 106.5, 115.0]
    h = [110.2, 113.5, 107.2, 106.9, 115.2]
    low = [99.8, 111.5, 105.8, 106.3, 107.8]
    assert _mh(_WO + o, _WH + h, _WL + low, _WC + c, penetration=0.5)[18] == 100.0
    assert _mh(_WO + o, _WH + h, _WL + low, _WC + c, penetration=0.3)[18] == 0.0


def test_mat_hold_warmup_is_zero():
    # The first 14 bars are always 0 (TA-Lib lookback = max(BodyShort, BodyLong) + 4 = 14).
    out = _mh(_WO + _BULL_O, _WH + _BULL_H, _WL + _BULL_L, _WC + _BULL_C)
    np.testing.assert_array_equal(out[:14], 0.0)


def test_mat_hold_constant_frame_is_zero():
    # A perfectly flat frame (all OHLC equal) has no long body and no gap -> all zeros.
    flat = [100.0] * 30
    out = INDICATORS.create("mat_hold").compute(frame(flat))["mat_hold"]
    np.testing.assert_array_equal(out.to_numpy(), 0.0)


def test_mat_hold_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros, no IndexError.
    short = [100.0, 101.0, 102.0, 101.0, 103.0]
    out = INDICATORS.create("mat_hold").compute(frame(short))["mat_hold"]
    np.testing.assert_array_equal(out.to_numpy(), 0.0)


def test_mat_hold_output_contract():
    out = INDICATORS.create("mat_hold").compute(
        frame(_WC + _BULL_C, high=_WH + _BULL_H, low=_WL + _BULL_L, open_=_WO + _BULL_O)
    )
    assert list(out.columns) == ["mat_hold"]
    # Mat Hold is purely bullish: values are only {0, 100} (no bearish or partial ±80 score).
    assert set(np.unique(out["mat_hold"].to_numpy())) <= {0.0, 100.0}


def test_mat_hold_rejects_unknown_param():
    with pytest.raises((TypeError, ValueError)):
        INDICATORS.create("mat_hold", not_a_param=1.0)
