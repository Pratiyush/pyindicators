"""Identical Three Crows — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.identical_three_crows import (
    identical_three_crows,  # noqa: F401  (fires @register)
)

# 12 warm-up bars with a 4.0 high-low range so the ShadowVeryShort average is ~0.4 and the
# Equal band ~0.2 by the time the pattern forms; the three crows (bars 12-14) are black with
# tiny lower shadows, declining closes, and open exactly at the prior crow's close.
_WARM = 12
_WO = [100.0] * _WARM
_WC = [101.0] * _WARM
_WH = [103.0] * _WARM
_WL = [99.0] * _WARM


def _i3c(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("identical_three_crows").compute(df)["identical_three_crows"].to_numpy()


def _pattern():
    # crows 12/13/14: black, declining closes, each opening at the prior crow's close (the
    # "identical" opens), each with a tiny 0.01 lower shadow so they pass ShadowVeryShort.
    o = _WO + [110.0, 108.0, 106.0]
    c = _WC + [108.0, 106.0, 104.0]
    h = _WH + [110.1, 108.1, 106.1]
    low = _WL + [107.99, 105.99, 103.99]
    return o, h, low, c


def test_identical_three_crows_golden_hit():
    o, h, low, c = _pattern()
    out = _i3c(o, h, low, c)
    assert out[14] == -100.0


def test_identical_three_crows_warmup_is_zero():
    o, h, low, c = _pattern()
    np.testing.assert_array_equal(_i3c(o, h, low, c)[:12], 0.0)  # TA-Lib lookback = 12


def test_identical_three_crows_third_crow_must_be_black():
    # Turn the third crow white (close > open) -> no pattern.
    o, h, low, c = _pattern()
    o[14], c[14] = 104.0, 106.0
    assert _i3c(o, h, low, c)[14] == 0.0


def test_identical_three_crows_opens_must_be_identical():
    # 3rd crow opens far above the 2nd crow's close (outside the Equal band) -> no pattern.
    o, h, low, c = _pattern()
    o[14] = 109.0
    assert _i3c(o, h, low, c)[14] == 0.0


def test_identical_three_crows_closes_must_decline():
    # 3rd crow closes above the 2nd crow (no longer progressively lower) -> no pattern.
    o, h, low, c = _pattern()
    o[14], c[14] = 107.5, 107.0
    assert _i3c(o, h, low, c)[14] == 0.0


def test_identical_three_crows_long_lower_shadow_blocks():
    # Give the 3rd crow a long lower shadow (low well below close) -> ShadowVeryShort fails.
    o, h, low, c = _pattern()
    low[14] = 100.0
    assert _i3c(o, h, low, c)[14] == 0.0


def test_identical_three_crows_short_frame_is_zero():
    # Frame shorter than the 12-bar lookback -> all zeros, never NaN.
    n = 8
    o = [100.0] * n
    c = [99.0] * n
    h = [100.5] * n
    low = [98.5] * n
    out = _i3c(o, h, low, c)
    assert out.shape == (n,)
    np.testing.assert_array_equal(out, 0.0)


def test_identical_three_crows_constant_frame_is_zero():
    # A constant (doji) frame has no black candles -> all zeros, never NaN.
    c = [100.0] * 40
    out = (
        INDICATORS.create("identical_three_crows")
        .compute(frame(c))["identical_three_crows"]
        .to_numpy()
    )
    np.testing.assert_array_equal(out, 0.0)


def test_identical_three_crows_output_contract():
    o, h, low, c = _pattern()
    out = INDICATORS.create("identical_three_crows").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["identical_three_crows"]
    vals = set(np.unique(out["identical_three_crows"].to_numpy()))
    assert vals <= {-100.0, -80.0, 0.0, 80.0, 100.0}
