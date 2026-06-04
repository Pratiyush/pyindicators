"""In-Neck — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.in_neck import in_neck  # noqa: F401  (import fires @register)

# 11 warm-up bars (small white bodies, body 0.4) so the BodyLong average is ~0.4 and the Equal
# average is a small fraction of the ~0.8 range by the time the pattern forms at bar 11 -> 12.
_WARM = 11
_WO = [100.0] * _WARM
_WC = [100.4] * _WARM
_WH = [100.6] * _WARM
_WL = [99.8] * _WARM


def _inn(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("in_neck").compute(df)["in_neck"].to_numpy()


def test_in_neck_bearish_hit():
    # Long black candle (108 -> 100), then a white candle that gaps below the prior low (opens
    # 99.0 < 99.5) and closes right at the prior close (100.0) -> bearish In-Neck = -100.
    o = _WO + [108.0, 99.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [108.5, 100.3]
    low = _WL + [99.5, 98.5]
    assert _inn(o, h, low, c)[12] == -100.0


def test_in_neck_no_gap_down_is_zero():
    # Same long black candle, but the white candle opens *above* the prior low (99.7 > 99.5):
    # no downward gap -> not an In-Neck -> 0.
    o = _WO + [108.0, 99.7]
    c = _WC + [100.0, 100.0]
    h = _WH + [108.5, 100.3]
    low = _WL + [99.5, 99.6]
    assert _inn(o, h, low, c)[12] == 0.0


def test_in_neck_close_too_deep_is_zero():
    # White candle closes well above the prior close (101.5, far past the Equal tolerance):
    # the penetration is too deep for an In-Neck -> 0.
    o = _WO + [108.0, 99.0]
    c = _WC + [100.0, 101.5]
    h = _WH + [108.5, 101.8]
    low = _WL + [99.5, 98.5]
    assert _inn(o, h, low, c)[12] == 0.0


def test_in_neck_constant_frame_is_zero():
    # A flat frame (open == close, zero bodies) can never form the pattern.
    flat = [100.0] * 30
    out = _inn(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_in_neck_short_frame_is_zero():
    # Fewer bars than the lookback (11): every output must be 0.
    o = [108.0, 99.0, 100.0]
    c = [100.0, 100.0, 100.0]
    h = [108.5, 100.3, 100.3]
    low = [99.5, 98.5, 98.5]
    np.testing.assert_array_equal(_inn(o, h, low, c), 0.0)


def test_in_neck_warmup_is_zero():
    o = _WO + [108.0, 99.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [108.5, 100.3]
    low = _WL + [99.5, 98.5]
    np.testing.assert_array_equal(_inn(o, h, low, c)[:11], 0.0)  # TA-Lib lookback = 11


def test_in_neck_output_contract():
    o = _WO + [108.0, 99.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [108.5, 100.3]
    low = _WL + [99.5, 98.5]
    out = INDICATORS.create("in_neck").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["in_neck"]
    assert set(np.unique(out["in_neck"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
