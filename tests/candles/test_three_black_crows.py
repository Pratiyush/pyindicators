"""Three Black Crows — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.three_black_crows import (
    three_black_crows,  # noqa: F401  (fires @register)
)

# 10 warm-up bars with a 4.0 high-low range so the ShadowVeryShort average is ~0.4 by the time
# the pattern forms; the three crows (bars 11-13) carry tiny 0.1 lower shadows so they pass.
_WARM = 10
_WO = [100.0] * _WARM
_WC = [101.0] * _WARM
_WH = [103.0] * _WARM
_WL = [99.0] * _WARM


def _tbc(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("three_black_crows").compute(df)["three_black_crows"].to_numpy()


def _pattern():
    # bar10 (i-3): white, high 110.7 tops crow1's close (106). crows 11/12/13: black, declining
    # closes, each opening inside the prior body, each with a 0.1 lower shadow.
    o = _WO + [100.0, 109.0, 108.0, 106.0]
    c = _WC + [110.5, 106.0, 104.0, 102.0]
    h = _WH + [110.7, 109.1, 108.1, 106.1]
    low = _WL + [99.5, 105.9, 103.9, 101.9]
    return o, h, low, c


def test_three_black_crows_golden_hit():
    o, h, low, c = _pattern()
    out = _tbc(o, h, low, c)
    assert out[13] == -100.0


def test_three_black_crows_warmup_is_zero():
    o, h, low, c = _pattern()
    np.testing.assert_array_equal(_tbc(o, h, low, c)[:13], 0.0)  # TA-Lib lookback = 13


def test_three_black_crows_prior_white_required():
    # Make the prior candle (bar 10) black instead of white -> no pattern.
    o, h, low, c = _pattern()
    o[10], c[10] = 102.0, 100.5
    assert _tbc(o, h, low, c)[13] == 0.0


def test_three_black_crows_third_crow_must_be_black():
    # Turn the third crow white (close > open) -> no pattern.
    o, h, low, c = _pattern()
    o[13], c[13] = 101.0, 103.0
    assert _tbc(o, h, low, c)[13] == 0.0


def test_three_black_crows_opens_must_be_within_prior_body():
    # Crow 2 opens above crow 1's open (not inside the body) -> no pattern.
    o, h, low, c = _pattern()
    o[12] = 109.5
    assert _tbc(o, h, low, c)[13] == 0.0


def test_three_black_crows_closes_must_decline():
    # Crow 3 closes above crow 2 (no longer progressively lower) -> no pattern.
    o, h, low, c = _pattern()
    c[13] = 104.5
    assert _tbc(o, h, low, c)[13] == 0.0


def test_three_black_crows_short_frame_is_zero():
    # Frame shorter than the 13-bar lookback -> all zeros.
    n = 8
    o = [100.0] * n
    c = [99.0] * n
    h = [100.5] * n
    low = [98.5] * n
    out = _tbc(o, h, low, c)
    assert out.shape == (n,)
    np.testing.assert_array_equal(out, 0.0)


def test_three_black_crows_constant_frame_is_zero():
    # A constant (doji) frame has no black candles -> all zeros, never NaN.
    c = [100.0] * 40
    out = INDICATORS.create("three_black_crows").compute(frame(c))["three_black_crows"].to_numpy()
    np.testing.assert_array_equal(out, 0.0)


def test_three_black_crows_output_contract():
    o, h, low, c = _pattern()
    out = INDICATORS.create("three_black_crows").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["three_black_crows"]
    assert set(np.unique(out["three_black_crows"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
