"""Three White Soldiers — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.candles.three_white_soldiers import (  # noqa: F401  (import fires @register)
    three_white_soldiers,
)

# 12 warm-up bars (small white bodies, range ~0.7) so ShadowVeryShort/BodyShort/Near/Far
# averages are settled by the time the three soldiers form at bars 12, 13, 14.
_WARM = 12
_WO = [100.0] * _WARM
_WC = [100.5] * _WARM
_WH = [100.6] * _WARM
_WL = [99.9] * _WARM


def _tws(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("three_white_soldiers").compute(df)["three_white_soldiers"].to_numpy()


def test_three_white_soldiers_golden_hit():
    # Three rising long white candles, each opening inside the prior body, tiny upper shadows.
    o = _WO + [101.0, 103.0, 105.0]
    c = _WC + [104.0, 106.0, 108.0]
    h = _WH + [104.05, 106.05, 108.05]
    low = _WL + [100.9, 102.9, 104.9]
    out = _tws(o, h, low, c)
    assert out[14] == 100.0


def test_three_white_soldiers_black_candle_is_zero():
    # Middle candle is black (open above close) -> not three white -> 0.
    o = _WO + [101.0, 106.0, 105.0]
    c = _WC + [104.0, 105.0, 108.0]
    h = _WH + [104.05, 106.05, 108.05]
    low = _WL + [100.9, 104.9, 104.9]
    out = _tws(o, h, low, c)
    assert out[14] == 0.0


def test_three_white_soldiers_long_upper_shadow_is_zero():
    # Third candle has a long upper shadow (close far below the high) -> 0.
    o = _WO + [101.0, 103.0, 105.0]
    c = _WC + [104.0, 106.0, 108.0]
    h = _WH + [104.05, 106.05, 112.0]  # huge upper shadow on the third bar
    low = _WL + [100.9, 102.9, 104.9]
    out = _tws(o, h, low, c)
    assert out[14] == 0.0


def test_three_white_soldiers_not_higher_close_is_zero():
    # Closes do not strictly rise (3rd close <= 2nd close) -> 0.
    o = _WO + [101.0, 103.0, 104.0]
    c = _WC + [104.0, 106.0, 106.0]
    h = _WH + [104.05, 106.05, 106.05]
    low = _WL + [100.9, 102.9, 103.9]
    out = _tws(o, h, low, c)
    assert out[14] == 0.0


def test_three_white_soldiers_warmup_is_zero():
    o = _WO + [101.0, 103.0, 105.0]
    c = _WC + [104.0, 106.0, 108.0]
    h = _WH + [104.05, 106.05, 108.05]
    low = _WL + [100.9, 102.9, 104.9]
    out = _tws(o, h, low, c)
    np.testing.assert_array_equal(out[:12], 0.0)  # TA-Lib lookback = 12


def test_three_white_soldiers_constant_frame_is_zero():
    # A perfectly flat frame: zero-length bodies are not white soldiers -> all 0.
    flat = [100.0] * 40
    out = _tws(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_three_white_soldiers_short_frame_is_zero():
    # Fewer bars than the lookback -> all 0, no IndexError.
    o = [100.0, 101.0, 102.0]
    c = [101.0, 102.0, 103.0]
    h = [101.05, 102.05, 103.05]
    low = [99.9, 100.9, 101.9]
    out = _tws(o, h, low, c)
    np.testing.assert_array_equal(out, 0.0)


def test_three_white_soldiers_output_contract():
    df = deterministic_frame()
    out = INDICATORS.create("three_white_soldiers").compute(df)
    assert list(out.columns) == ["three_white_soldiers"]
    # Bullish-only pattern: only 0 or +100 ever appear.
    assert set(np.unique(out["three_white_soldiers"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
