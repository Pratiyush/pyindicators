"""Counterattack — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.counterattack import counterattack  # noqa: F401 (import fires @register)

# 11 warm-up bars (body 2.0) so the BodyLong average is 2.0 and the Equal average (5-bar
# HighLow of 0.4) is ~0.02 by the time the pattern forms at bar 11 -> bar 12.
_WARM = 11
_WO = [100.0] * _WARM
_WC = [102.0] * _WARM
_WH = [102.2] * _WARM
_WL = [99.8] * _WARM


def _cca(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("counterattack").compute(df)["counterattack"].to_numpy()


def test_counterattack_bullish():
    # Long black (108->100), then long white (92->100) closing right back at 100 -> +100.
    o = _WO + [108.0, 92.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [108.5, 100.5]
    low = _WL + [99.5, 91.5]
    assert _cca(o, h, low, c)[12] == 100.0


def test_counterattack_bearish():
    # Long white (100->108), then long black (116->108) closing right back at 108 -> -100.
    o = _WO + [100.0, 116.0]
    c = _WC + [108.0, 108.0]
    h = _WH + [108.5, 116.5]
    low = _WL + [99.5, 107.5]
    assert _cca(o, h, low, c)[12] == -100.0


def test_counterattack_same_color_is_zero():
    # Both white (long bodies, equal closes) -> not opposite colours -> 0.
    o = _WO + [92.0, 92.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [100.5, 100.5]
    low = _WL + [91.5, 91.5]
    assert _cca(o, h, low, c)[12] == 0.0


def test_counterattack_closes_far_apart_is_zero():
    # Opposite colours, both long, but second close far from the first -> 0.
    o = _WO + [108.0, 92.0]
    c = _WC + [100.0, 105.0]
    h = _WH + [108.5, 105.5]
    low = _WL + [99.5, 91.5]
    assert _cca(o, h, low, c)[12] == 0.0


def test_counterattack_short_second_body_is_zero():
    # First long black, second white but a tiny body (not long) -> 0.
    o = _WO + [108.0, 100.05]
    c = _WC + [100.0, 100.0]
    h = _WH + [108.5, 100.2]
    low = _WL + [99.5, 99.85]
    assert _cca(o, h, low, c)[12] == 0.0


def test_counterattack_warmup_is_zero():
    o = _WO + [108.0, 92.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [108.5, 100.5]
    low = _WL + [99.5, 91.5]
    np.testing.assert_array_equal(_cca(o, h, low, c)[:11], 0.0)  # TA-Lib lookback = 11


def test_counterattack_constant_frame_is_zero():
    # A flat doji frame (open == close) has no long bodies anywhere -> all zeros.
    flat = [100.0] * 40
    out = _cca(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_counterattack_short_frame_is_zero():
    # Frames shorter than the lookback must be all zeros.
    o = [108.0, 92.0, 100.0]
    c = [100.0, 100.0, 92.0]
    h = [108.5, 100.5, 100.5]
    low = [99.5, 91.5, 91.5]
    np.testing.assert_array_equal(_cca(o, h, low, c), 0.0)


def test_counterattack_output_contract():
    o = _WO + [108.0, 92.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [108.5, 100.5]
    low = _WL + [99.5, 91.5]
    out = INDICATORS.create("counterattack").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["counterattack"]
    assert set(np.unique(out["counterattack"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
