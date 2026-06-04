"""Doji Star — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.doji_star import doji_star  # noqa: F401  (import fires @register)

# 11 warm-up bars (body 2.0) so the BodyLong average is 2.0 by the time the long body forms at
# bar 11 -> the doji star completes at bar 12.
_WARM = 11
_WO = [100.0] * _WARM
_WC = [102.0] * _WARM
_WH = [102.2] * _WARM
_WL = [99.8] * _WARM


def _star(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("doji_star").compute(df)["doji_star"].to_numpy()


def test_doji_star_bearish_after_white():
    # Long white body (100->110) then a doji gapping up above it -> -100 (prev white).
    o = _WO + [100.0, 113.0]
    c = _WC + [110.0, 113.05]
    h = _WH + [110.5, 113.6]
    low = _WL + [99.5, 112.6]
    assert _star(o, h, low, c)[12] == -100.0


def test_doji_star_bullish_after_black():
    # Long black body (110->100) then a doji gapping down below it -> +100 (prev black).
    o = _WO + [110.0, 97.0]
    c = _WC + [100.0, 96.95]
    h = _WH + [110.5, 97.5]
    low = _WL + [99.5, 96.4]
    assert _star(o, h, low, c)[12] == 100.0


def test_doji_star_no_gap_is_zero():
    # Long white body then a doji that overlaps (no real-body gap up) -> 0.
    o = _WO + [100.0, 109.0]
    c = _WC + [110.0, 109.05]
    h = _WH + [110.5, 109.6]
    low = _WL + [99.5, 108.6]
    assert _star(o, h, low, c)[12] == 0.0


def test_doji_star_not_doji_is_zero():
    # Long white body then a gapping-up but *large* second body (not a doji) -> 0.
    o = _WO + [100.0, 113.0]
    c = _WC + [110.0, 117.0]
    h = _WH + [110.5, 117.5]
    low = _WL + [99.5, 112.5]
    assert _star(o, h, low, c)[12] == 0.0


def test_doji_star_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (no warm-up to form an average).
    o = [100.0, 113.0, 114.0]
    c = [110.0, 113.05, 114.05]
    h = [110.5, 113.6, 114.6]
    low = [99.5, 112.6, 113.6]
    np.testing.assert_array_equal(_star(o, h, low, c), 0.0)


def test_doji_star_constant_frame_is_zero():
    # A flat constant frame has no long body and no gaps -> all zeros.
    c = [100.0] * 30
    out = INDICATORS.create("doji_star").compute(frame(c)).to_numpy()
    np.testing.assert_array_equal(out, 0.0)


def test_doji_star_warmup_is_zero():
    o = _WO + [100.0, 113.0]
    c = _WC + [110.0, 113.05]
    h = _WH + [110.5, 113.6]
    low = _WL + [99.5, 112.6]
    np.testing.assert_array_equal(_star(o, h, low, c)[:11], 0.0)  # TA-Lib lookback = 11


def test_doji_star_output_contract():
    o = _WO + [100.0, 113.0]
    c = _WC + [110.0, 113.05]
    h = _WH + [110.5, 113.6]
    low = _WL + [99.5, 112.6]
    out = INDICATORS.create("doji_star").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["doji_star"]
    assert set(np.unique(out["doji_star"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
