"""Dark Cloud Cover — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.dark_cloud_cover import dark_cloud_cover  # noqa: F401  (fires register)

# 11 warm-up bars (body 1.0) so the BodyLong average is small (1.0) by the time the pattern
# can form at bar 11 -> bar 12.
_WARM = 11
_WO = [100.0] * _WARM
_WC = [101.0] * _WARM
_WH = [101.2] * _WARM
_WL = [99.8] * _WARM


def _dcc(o, h, low, c, **kw):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("dark_cloud_cover", **kw).compute(df)["dark_cloud_cover"].to_numpy()


def test_dark_cloud_cover_fires_minus_100():
    # bar11 long white (100->110, body 10 > avg 1.0); bar12 black opens 112 (> prior high
    # 110.5), closes 104 (> prior open 100, and < 110 - 10*0.5 = 105) -> -100.
    o = _WO + [100.0, 112.0]
    c = _WC + [110.0, 104.0]
    h = _WH + [110.5, 112.5]
    low = _WL + [99.5, 103.5]
    assert _dcc(o, h, low, c)[12] == -100.0


def test_dark_cloud_cover_no_gap_is_zero():
    # Black candle opens at/below the prior high (109 <= 110.5) -> not a dark cloud -> 0.
    o = _WO + [100.0, 109.0]
    c = _WC + [110.0, 104.0]
    h = _WH + [110.5, 109.5]
    low = _WL + [99.5, 103.5]
    assert _dcc(o, h, low, c)[12] == 0.0


def test_dark_cloud_cover_shallow_penetration_is_zero():
    # Close 106 does not pierce past 110 - 10*0.5 = 105 -> 0.
    o = _WO + [100.0, 112.0]
    c = _WC + [110.0, 106.0]
    h = _WH + [110.5, 112.5]
    low = _WL + [99.5, 105.5]
    assert _dcc(o, h, low, c)[12] == 0.0


def test_dark_cloud_cover_below_prior_open_is_zero():
    # Close 99 < prior open 100 is an *engulfing*-style breach, not a dark cloud -> 0.
    o = _WO + [100.0, 112.0]
    c = _WC + [110.0, 99.0]
    h = _WH + [110.5, 112.5]
    low = _WL + [99.5, 98.5]
    assert _dcc(o, h, low, c)[12] == 0.0


def test_dark_cloud_cover_penetration_param_loosens():
    # Close 106 doesn't pierce at pen=0.5 (threshold 105) but does at pen=0.3 (threshold 107).
    o = _WO + [100.0, 112.0]
    c = _WC + [110.0, 106.0]
    h = _WH + [110.5, 112.5]
    low = _WL + [99.5, 105.5]
    assert _dcc(o, h, low, c, penetration=0.5)[12] == 0.0
    assert _dcc(o, h, low, c, penetration=0.3)[12] == -100.0


def test_dark_cloud_cover_constant_frame_is_zero():
    # A flat (doji) series can never form the pattern (no long white body) -> all 0.
    flat = [100.0] * 30
    out = _dcc(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_dark_cloud_cover_short_frame_is_zero():
    # Fewer bars than the 11-bar lookback -> all 0, no error.
    c = [100.0, 110.0, 104.0, 108.0]
    o = [100.0, 100.0, 112.0, 105.0]
    h = [100.5, 110.5, 112.5, 108.5]
    low = [99.5, 99.5, 103.5, 104.5]
    out = _dcc(o, h, low, c)
    np.testing.assert_array_equal(out, 0.0)


def test_dark_cloud_cover_lookback_zeros_first_eleven():
    o = _WO + [100.0, 112.0]
    c = _WC + [110.0, 104.0]
    h = _WH + [110.5, 112.5]
    low = _WL + [99.5, 103.5]
    np.testing.assert_array_equal(_dcc(o, h, low, c)[:11], 0.0)  # TA-Lib lookback = 11


def test_dark_cloud_cover_output_contract():
    o = _WO + [100.0, 112.0]
    c = _WC + [110.0, 104.0]
    h = _WH + [110.5, 112.5]
    low = _WL + [99.5, 103.5]
    out = INDICATORS.create("dark_cloud_cover").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["dark_cloud_cover"]
    vals = set(np.unique(out["dark_cloud_cover"].to_numpy()))
    assert vals <= {-100.0, -80.0, 0.0, 80.0, 100.0}
