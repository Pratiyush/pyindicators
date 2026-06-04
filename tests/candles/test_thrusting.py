"""Thrusting — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.thrusting import thrusting  # noqa: F401  (import fires @register)

# 11 warm-up bars (small white bodies, body 0.4) so the BodyLong average is ~0.4 and the Equal
# average is a small fraction of the ~0.8 range by the time the pattern forms at bar 11 -> 12.
_WARM = 11
_WO = [100.0] * _WARM
_WC = [100.4] * _WARM
_WH = [100.6] * _WARM
_WL = [99.8] * _WARM


def _thr(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("thrusting").compute(df)["thrusting"].to_numpy()


def test_thrusting_bearish_hit():
    # Long black candle (108 -> 100), then a white candle that gaps below the prior low (opens
    # 99.0 < 99.5) and closes well into the prior body (102.0): above the prior close past the
    # Equal tolerance, yet below the prior body midpoint (104.0) -> bearish Thrusting = -100.
    o = _WO + [108.0, 99.0]
    c = _WC + [100.0, 102.0]
    h = _WH + [108.5, 102.3]
    low = _WL + [99.5, 98.5]
    assert _thr(o, h, low, c)[12] == -100.0


def test_thrusting_too_shallow_is_zero():
    # White candle closes right at the prior close (100.0, within the Equal band): the close is
    # too shallow for Thrusting (this is In-Neck territory) -> 0.
    o = _WO + [108.0, 99.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [108.5, 100.3]
    low = _WL + [99.5, 98.5]
    assert _thr(o, h, low, c)[12] == 0.0


def test_thrusting_past_midpoint_is_zero():
    # White candle closes past the prior body midpoint (105.0 > 104.0): too deep for Thrusting
    # (this is Piercing territory, a bullish reversal) -> 0.
    o = _WO + [108.0, 99.0]
    c = _WC + [100.0, 105.0]
    h = _WH + [108.5, 105.3]
    low = _WL + [99.5, 98.5]
    assert _thr(o, h, low, c)[12] == 0.0


def test_thrusting_no_gap_down_is_zero():
    # Same long black candle, but the white candle opens *above* the prior low (99.7 > 99.5):
    # no downward gap -> not a Thrusting -> 0.
    o = _WO + [108.0, 99.7]
    c = _WC + [100.0, 102.0]
    h = _WH + [108.5, 102.3]
    low = _WL + [99.5, 99.6]
    assert _thr(o, h, low, c)[12] == 0.0


def test_thrusting_constant_frame_is_zero():
    # A flat frame (open == close, zero bodies) can never form the pattern.
    flat = [100.0] * 30
    out = _thr(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_thrusting_short_frame_is_zero():
    # Fewer bars than the lookback (11): every output must be 0.
    o = [108.0, 99.0, 100.0]
    c = [100.0, 100.0, 102.0]
    h = [108.5, 100.3, 102.3]
    low = [99.5, 98.5, 98.5]
    np.testing.assert_array_equal(_thr(o, h, low, c), 0.0)


def test_thrusting_warmup_is_zero():
    o = _WO + [108.0, 99.0]
    c = _WC + [100.0, 102.0]
    h = _WH + [108.5, 102.3]
    low = _WL + [99.5, 98.5]
    np.testing.assert_array_equal(_thr(o, h, low, c)[:11], 0.0)  # TA-Lib lookback = 11


def test_thrusting_output_contract():
    o = _WO + [108.0, 99.0]
    c = _WC + [100.0, 102.0]
    h = _WH + [108.5, 102.3]
    low = _WL + [99.5, 98.5]
    out = INDICATORS.create("thrusting").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["thrusting"]
    assert set(np.unique(out["thrusting"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
