"""Stick Sandwich — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.stick_sandwich import (
    stick_sandwich,  # noqa: F401  (import fires @register)
)

# 5 warm-up bars with a tight high-low range so the Equal average (HighLow/5/0.05) is small;
# the three-candle pattern then forms at bars 5, 6, 7 (first possible fire at bar 7).
_WARM = 5
_WO = [100.0] * _WARM
_WC = [100.05] * _WARM
_WH = [100.1] * _WARM  # high-low = 0.2 -> Equal avg = 0.2 * 0.05 = 0.01 around close[i-2]
_WL = [99.9] * _WARM


def _ss(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("stick_sandwich").compute(df)["stick_sandwich"].to_numpy()


def test_stick_sandwich_bullish_strict():
    # black (110->100), white whose low (104) > first close (100), black closing back at 100.
    o = _WO + [110.0, 105.0, 103.0]
    c = _WC + [100.0, 115.0, 100.0]
    h = _WH + [110.0, 116.0, 118.0]
    low = _WL + [99.0, 104.0, 99.0]
    assert _ss(o, h, low, c)[7] == 100.0


def test_stick_sandwich_no_gap_required():
    # The third candle need NOT gap above the second high — only colours + low + close equality.
    o = _WO + [110.0, 105.0, 101.0]  # third opens well below the second's high (116)
    c = _WC + [100.0, 115.0, 100.0]
    h = _WH + [110.0, 116.0, 102.0]
    low = _WL + [99.0, 104.0, 99.0]
    assert _ss(o, h, low, c)[7] == 100.0


def test_stick_sandwich_middle_low_must_clear_first_close():
    # Second candle's low == first close (100) is NOT strictly above -> no pattern.
    o = _WO + [110.0, 105.0, 103.0]
    c = _WC + [100.0, 115.0, 100.0]
    h = _WH + [110.0, 116.0, 118.0]
    low = _WL + [99.0, 100.0, 99.0]  # low2 == close1, equality fails the strict ">"
    assert _ss(o, h, low, c)[7] == 0.0


def test_stick_sandwich_third_close_must_match_first():
    # Third close far from the first close (outside the tiny Equal band) -> no pattern.
    o = _WO + [110.0, 105.0, 103.0]
    c = _WC + [100.0, 115.0, 98.0]  # 98 is well below 100 - Equal avg (0.01)
    h = _WH + [110.0, 116.0, 118.0]
    low = _WL + [99.0, 104.0, 97.0]
    assert _ss(o, h, low, c)[7] == 0.0


def test_stick_sandwich_wrong_colors():
    # Middle candle black (not white) breaks the black/white/black sequence -> no pattern.
    o = _WO + [110.0, 115.0, 103.0]
    c = _WC + [100.0, 105.0, 100.0]  # middle is black (open > close)
    h = _WH + [110.0, 116.0, 118.0]
    low = _WL + [99.0, 104.0, 99.0]
    assert _ss(o, h, low, c)[7] == 0.0


def test_stick_sandwich_warmup_is_zero():
    o = _WO + [110.0, 105.0, 103.0]
    c = _WC + [100.0, 115.0, 100.0]
    h = _WH + [110.0, 116.0, 118.0]
    low = _WL + [99.0, 104.0, 99.0]
    np.testing.assert_array_equal(_ss(o, h, low, c)[:7], 0.0)  # TA-Lib lookback = 7


def test_stick_sandwich_constant_frame_is_zero():
    # A flat frame (all bars identical, zero range) is never a stick sandwich.
    flat = [50.0] * 20
    out = _ss(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_stick_sandwich_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (no room for the pattern).
    o = [100.0, 110.0, 105.0, 103.0]
    c = [100.0, 100.0, 115.0, 100.0]
    h = [100.1, 110.0, 116.0, 118.0]
    low = [99.9, 99.0, 104.0, 99.0]
    out = _ss(o, h, low, c)
    np.testing.assert_array_equal(out, 0.0)


def test_stick_sandwich_output_contract():
    o = _WO + [110.0, 105.0, 103.0]
    c = _WC + [100.0, 115.0, 100.0]
    h = _WH + [110.0, 116.0, 118.0]
    low = _WL + [99.0, 104.0, 99.0]
    out = INDICATORS.create("stick_sandwich").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["stick_sandwich"]
    assert set(np.unique(out["stick_sandwich"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
