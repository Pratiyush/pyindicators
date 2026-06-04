"""Matching Low — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.matching_low import matching_low  # noqa: F401  (import fires @register)

# 6 warm-up bars so the previous-bar Equal (HighLow/5/0.05) average is defined by the time the
# pattern can form at bar index 6. A 1.0-wide range gives Equal average = 0.05 * 1.0 = 0.05.
_WARM = 6
_WO = [100.0] * _WARM
_WC = [99.5] * _WARM
_WH = [100.5] * _WARM
_WL = [99.0] * _WARM


def _ml(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("matching_low").compute(df)["matching_low"].to_numpy()


def test_matching_low_two_black_equal_closes_is_100():
    # Two black candles (open > close) with identical closes -> +100 at the second.
    o = _WO + [105.0, 103.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [105.5, 103.5]
    low = _WL + [99.5, 99.5]
    assert _ml(o, h, low, c)[7] == 100.0


def test_matching_low_closes_within_equal_band_is_100():
    # Second close differs by 0.04 < Equal average (0.05 from the ~1.0-wide warm-up range) -> 100.
    o = _WO + [105.0, 103.0]
    c = _WC + [100.0, 100.04]
    h = _WH + [105.5, 103.5]
    low = _WL + [99.5, 99.5]
    assert _ml(o, h, low, c)[7] == 100.0


def test_matching_low_closes_outside_equal_band_is_0():
    # Second close differs by 0.5 (well beyond the Equal tolerance) -> no pattern.
    o = _WO + [105.0, 103.0]
    c = _WC + [100.0, 100.5]
    h = _WH + [105.5, 103.5]
    low = _WL + [99.5, 100.0]
    assert _ml(o, h, low, c)[7] == 0.0


def test_matching_low_first_white_is_0():
    # First candle white (close > open) -> not the pattern even with equal closes.
    o = _WO + [98.0, 103.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [100.5, 103.5]
    low = _WL + [97.5, 99.5]
    assert _ml(o, h, low, c)[7] == 0.0


def test_matching_low_second_white_is_0():
    # Second candle white (close > open) -> not the pattern even with equal closes.
    o = _WO + [105.0, 99.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [105.5, 100.5]
    low = _WL + [99.5, 98.5]
    assert _ml(o, h, low, c)[7] == 0.0


def test_matching_low_constant_frame_is_zero():
    # A flat frame: open == close everywhere -> candles are "white" (close >= open) -> all 0.
    flat = [50.0] * 40
    out = _ml(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_matching_low_short_frame_is_zero():
    # Frames shorter than the lookback (6) can never signal.
    for length in range(0, 7):
        o = [105.0] * length
        c = [100.0] * length
        h = [105.5] * length
        low = [99.5] * length
        out = _ml(o, h, low, c)
        assert out.shape == (length,)
        np.testing.assert_array_equal(out, 0.0)


def test_matching_low_warmup_is_zero():
    o = _WO + [105.0, 103.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [105.5, 103.5]
    low = _WL + [99.5, 99.5]
    np.testing.assert_array_equal(_ml(o, h, low, c)[:6], 0.0)  # TA-Lib lookback = 6


def test_matching_low_output_contract():
    o = _WO + [105.0, 103.0]
    c = _WC + [100.0, 100.0]
    h = _WH + [105.5, 103.5]
    low = _WL + [99.5, 99.5]
    out = INDICATORS.create("matching_low").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["matching_low"]
    assert set(np.unique(out["matching_low"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
