"""Two Crows — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.two_crows import two_crows  # noqa: F401  (import fires @register)

# 12 warm-up white bars (body 100->102) so the BodyLong average is ~2.0 by the time the
# pattern can first form (third bar at index 14; TA-Lib lookback = 12).
_WARM = 12
_WO = [100.0] * _WARM
_WC = [102.0] * _WARM
_WH = [102.5] * _WARM
_WL = [99.5] * _WARM


def _two_crows(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("two_crows").compute(df)["two_crows"].to_numpy()


def _canonical():
    # 1st (idx12): long WHITE 100->110 (body 100..110).
    # 2nd (idx13): BLACK gapping up, body 112..115 (bottom 112 > 1st top 110).
    # 3rd (idx14): BLACK opens 114 (within 112..115) and closes 105 (within 100..110) -> -100.
    o = _WO + [100.0, 115.0, 114.0]
    h = _WH + [110.5, 115.5, 114.2]
    low = _WL + [99.5, 111.5, 104.5]
    c = _WC + [110.0, 112.0, 105.0]
    return o, h, low, c


def test_two_crows_bearish_strict():
    assert _two_crows(*_canonical())[14] == -100.0


def test_two_crows_no_gap_is_zero():
    # 2nd candle body bottom merely touches the 1st body top (110): gap is strict -> 0.
    o = _WO + [100.0, 115.0, 114.0]
    h = _WH + [110.5, 115.5, 114.2]
    low = _WL + [99.5, 110.0, 104.5]
    c = _WC + [110.0, 110.0, 105.0]
    assert _two_crows(o, h, low, c)[14] == 0.0


def test_two_crows_third_not_black_is_zero():
    # Make the 3rd candle white (open below close): not a crow -> 0.
    o = _WO + [100.0, 115.0, 104.0]
    h = _WH + [110.5, 115.5, 114.2]
    low = _WL + [99.5, 111.5, 103.5]
    c = _WC + [110.0, 112.0, 113.0]
    assert _two_crows(o, h, low, c)[14] == 0.0


def test_two_crows_close_outside_first_is_zero():
    # 3rd closes below the 1st body open (100): not "within the 1st body" -> 0.
    o = _WO + [100.0, 115.0, 114.0]
    h = _WH + [110.5, 115.5, 114.2]
    low = _WL + [99.5, 111.5, 98.5]
    c = _WC + [110.0, 112.0, 99.0]
    assert _two_crows(o, h, low, c)[14] == 0.0


def test_two_crows_constant_frame_is_zero():
    # A flat frame (all bars identical, zero bodies) never forms the pattern.
    flat = [100.0] * 30
    np.testing.assert_array_equal(_two_crows(flat, flat, flat, flat), 0.0)


def test_two_crows_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (no room for the pattern).
    o = [100.0, 110.0, 115.0, 114.0]
    h = [100.5, 110.5, 115.5, 114.2]
    low = [99.5, 99.5, 111.5, 104.5]
    c = [100.0, 110.0, 112.0, 105.0]
    np.testing.assert_array_equal(_two_crows(o, h, low, c), 0.0)


def test_two_crows_warmup_is_zero():
    o, h, low, c = _canonical()
    np.testing.assert_array_equal(_two_crows(o, h, low, c)[:12], 0.0)  # TA-Lib lookback = 12


def test_two_crows_output_contract():
    o, h, low, c = _canonical()
    out = INDICATORS.create("two_crows").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["two_crows"]
    assert set(np.unique(out["two_crows"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
