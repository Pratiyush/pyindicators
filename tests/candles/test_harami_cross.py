"""Harami Cross — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.harami_cross import harami_cross  # noqa: F401  (import fires @register)

# 11 warm-up bars (body 2.0) so BodyLong is 2.0 and BodyDoji (10% of HighLow ~2.4) ~0.24 by the
# time the pattern forms at bar 12 -> bar 13.
_WARM = 11
_WO = [100.0] * _WARM
_WC = [102.0] * _WARM
_WH = [102.2] * _WARM
_WL = [99.8] * _WARM


def _har(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("harami_cross").compute(df)["harami_cross"].to_numpy()


def test_harami_cross_bullish_strict():
    # Long black (110->100) then a doji (open == close == 105) strictly inside -> +100.
    o = _WO + [110.0, 105.0]
    c = _WC + [100.0, 105.0]
    h = _WH + [110.5, 105.5]
    low = _WL + [99.5, 104.5]
    assert _har(o, h, low, c)[12] == 100.0


def test_harami_cross_bearish_strict():
    # Long white (100->110) then a doji (open == close == 105) strictly inside -> -100.
    o = _WO + [100.0, 105.0]
    c = _WC + [110.0, 105.0]
    h = _WH + [110.5, 105.5]
    low = _WL + [99.5, 104.5]
    assert _har(o, h, low, c)[12] == -100.0


def test_harami_cross_one_edge_touch_is_80():
    # Doji whose body touches the previous body's top edge (strict bottom) -> partial score 80.
    # Previous long black 110->100 (body_hi=110, body_lo=100); doji at exactly 110 (top tie).
    o = _WO + [110.0, 110.0]
    c = _WC + [100.0, 110.0]
    h = _WH + [110.5, 110.5]
    low = _WL + [99.5, 109.8]
    assert _har(o, h, low, c)[12] == 80.0


def test_harami_cross_short_body_not_doji_is_zero():
    # A small but non-doji body (body 1.0, well above BodyDoji ~0.24) inside long prev -> 0.
    o = _WO + [110.0, 104.5]
    c = _WC + [100.0, 105.5]
    h = _WH + [110.5, 105.7]
    low = _WL + [99.5, 104.3]
    assert _har(o, h, low, c)[12] == 0.0


def test_harami_cross_warmup_is_zero():
    o = _WO + [110.0, 105.0]
    c = _WC + [100.0, 105.0]
    h = _WH + [110.5, 105.5]
    low = _WL + [99.5, 104.5]
    np.testing.assert_array_equal(_har(o, h, low, c)[:11], 0.0)  # TA-Lib lookback = 11


def test_harami_cross_constant_frame_is_zero():
    # A constant flat frame has no long body anywhere -> all zeros.
    flat = [100.0] * 40
    out = _har(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_harami_cross_short_frame_is_zero():
    # Frame shorter than the lookback -> all zeros (average never warms up).
    o = [110.0, 105.0, 108.0]
    c = [100.0, 105.0, 101.0]
    h = [110.5, 105.5, 108.5]
    low = [99.5, 104.5, 100.5]
    np.testing.assert_array_equal(_har(o, h, low, c), 0.0)


def test_harami_cross_output_contract():
    o = _WO + [110.0, 105.0]
    c = _WC + [100.0, 105.0]
    h = _WH + [110.5, 105.5]
    low = _WL + [99.5, 104.5]
    out = INDICATORS.create("harami_cross").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["harami_cross"]
    uniq = set(np.unique(out["harami_cross"].to_numpy()))
    assert uniq <= {-100.0, -80.0, 0.0, 80.0, 100.0}
