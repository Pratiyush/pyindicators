"""Evening Doji Star — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.evening_doji_star import (
    evening_doji_star,  # noqa: F401  (fires @register)
)

# 12 warm-up bars (body 2.0) so BodyLong/BodyShort/BodyDoji averages are settled by the time the
# three-bar pattern forms at bars 12 -> 13 -> 14 (TA-Lib lookback = 12).
_WARM = 12
_WO = [100.0] * _WARM
_WC = [102.0] * _WARM
_WH = [102.2] * _WARM
_WL = [99.8] * _WARM


def _eds(o, h, low, c, penetration=None):
    df = frame(c, high=h, low=low, open_=o)
    if penetration is None:
        return INDICATORS.create("evening_doji_star").compute(df)["evening_doji_star"].to_numpy()
    ind = INDICATORS.create("evening_doji_star", penetration=penetration)
    return ind.compute(df)["evening_doji_star"].to_numpy()


def test_evening_doji_star_strict_bearish():
    # Long white (100->110), a doji gapping up (open=close=115), then a black candle closing
    # deep into the first white body (115->103) -> -100.
    o = _WO + [100.0, 115.0, 114.0]
    c = _WC + [110.0, 115.0, 103.0]
    h = _WH + [110.5, 115.5, 114.5]
    low = _WL + [99.5, 114.5, 102.5]
    assert _eds(o, h, low, c)[14] == -100.0


def test_evening_doji_star_shallow_close_is_zero():
    # Third candle closes only to 108 — not below close(1st) 110 - body(10) * 0.3 = 107 -> 0.
    o = _WO + [100.0, 115.0, 114.0]
    c = _WC + [110.0, 115.0, 108.0]
    h = _WH + [110.5, 115.5, 114.5]
    low = _WL + [99.5, 114.5, 107.5]
    assert _eds(o, h, low, c)[14] == 0.0


def test_evening_doji_star_no_gap_up_is_zero():
    # The doji does not gap up over the first body (sits at 109, below the 110 body top) -> 0.
    o = _WO + [100.0, 109.0, 108.0]
    c = _WC + [110.0, 109.0, 103.0]
    h = _WH + [110.5, 109.5, 108.5]
    low = _WL + [99.5, 108.5, 102.5]
    assert _eds(o, h, low, c)[14] == 0.0


def test_evening_doji_star_penetration_param():
    # A shallow close (108) is rejected at the default 0.3 but accepted at a small penetration:
    # 108 < close(1st) 110 - body(10) * 0.05 = 109.5 -> -100.
    o = _WO + [100.0, 115.0, 114.0]
    c = _WC + [110.0, 115.0, 108.0]
    h = _WH + [110.5, 115.5, 114.5]
    low = _WL + [99.5, 114.5, 107.5]
    assert _eds(o, h, low, c, penetration=0.3)[14] == 0.0
    assert _eds(o, h, low, c, penetration=0.05)[14] == -100.0


def test_evening_doji_star_warmup_is_zero():
    o = _WO + [100.0, 115.0, 114.0]
    c = _WC + [110.0, 115.0, 103.0]
    h = _WH + [110.5, 115.5, 114.5]
    low = _WL + [99.5, 114.5, 102.5]
    np.testing.assert_array_equal(_eds(o, h, low, c)[:12], 0.0)  # TA-Lib lookback = 12


def test_evening_doji_star_constant_frame_is_zero():
    # No real body anywhere -> the long-white-candle condition can never fire -> all zero.
    flat = [100.0] * 40
    out = _eds(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_evening_doji_star_short_frame_is_zero():
    # Frames at or below the 12-bar lookback are entirely 0 (no room for the pattern).
    c = list(range(100, 105))
    h = [x + 1 for x in c]
    low = [x - 1 for x in c]
    out = _eds(c, h, low, c)
    assert len(out) == len(c)
    np.testing.assert_array_equal(out, 0.0)


def test_evening_doji_star_extra_param_rejected():
    with pytest.raises(Exception):  # noqa: B017,PT011  (pydantic ValidationError, extra='forbid')
        INDICATORS.create("evening_doji_star", bogus=1)


def test_evening_doji_star_output_contract():
    o = _WO + [100.0, 115.0, 114.0]
    c = _WC + [110.0, 115.0, 103.0]
    h = _WH + [110.5, 115.5, 114.5]
    low = _WL + [99.5, 114.5, 102.5]
    out = INDICATORS.create("evening_doji_star").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["evening_doji_star"]
    values = set(np.unique(out["evening_doji_star"].to_numpy()))
    assert values <= {-100.0, -80.0, 0.0, 80.0, 100.0}
