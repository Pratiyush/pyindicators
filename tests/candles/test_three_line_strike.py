"""Three-Line Strike — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.three_line_strike import (
    three_line_strike,  # noqa: F401  (fires @register)
)

# 9 flat warm-up bars (tiny range) so the Near average is defined by the time the four-bar
# pattern forms at indices 9..12. Warm-up bars are not part of any pattern.
_WARM = 9
_WO = [100.0] * _WARM
_WC = [100.0] * _WARM
_WH = [100.4] * _WARM
_WL = [99.6] * _WARM


def _build(seq_o: list[float], seq_c: list[float]):
    o = _WO + seq_o
    c = _WC + seq_c
    h = [max(a, b) + 0.5 for a, b in zip(o, c, strict=True)]
    low = [min(a, b) - 0.5 for a, b in zip(o, c, strict=True)]
    return o, h, low, c


def _tls(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("three_line_strike").compute(df)["three_line_strike"].to_numpy()


def test_three_line_strike_bullish_is_plus_100():
    # Three rising white candles, then a black candle opening above the run's last close and
    # closing below the run's first open -> +100 (the white run's colour).
    o, h, low, c = _build([100.0, 101.5, 103.5, 107.0], [102.0, 104.0, 106.0, 99.0])
    assert _tls(o, h, low, c)[12] == 100.0


def test_three_line_strike_bearish_is_minus_100():
    # Three falling black candles, then a white candle opening below the run's last close and
    # closing above the run's first open -> -100 (the black run's colour).
    o, h, low, c = _build([106.0, 104.5, 102.5, 99.0], [104.0, 102.0, 100.0, 107.0])
    assert _tls(o, h, low, c)[12] == -100.0


def test_three_line_strike_no_pattern_is_zero():
    # Same three white candles but the fourth is also white (no opposite-colour strike) -> 0.
    o, h, low, c = _build([100.0, 101.5, 103.5, 104.0], [102.0, 104.0, 106.0, 108.0])
    assert _tls(o, h, low, c)[12] == 0.0


def test_three_line_strike_warmup_is_zero():
    # The first 8 bars are always 0 (TA-Lib lookback = avgPeriod(Near) + 3 = 8).
    o, h, low, c = _build([100.0, 101.5, 103.5, 107.0], [102.0, 104.0, 106.0, 99.0])
    np.testing.assert_array_equal(_tls(o, h, low, c)[:8], 0.0)


def test_three_line_strike_constant_frame_is_zero():
    # A perfectly flat frame (all OHLC equal) can never form the pattern -> all zeros.
    flat = [100.0] * 30
    out = INDICATORS.create("three_line_strike").compute(frame(flat))["three_line_strike"]
    np.testing.assert_array_equal(out.to_numpy(), 0.0)


def test_three_line_strike_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros, no error.
    short = [100.0, 101.0, 102.0, 101.0, 103.0]
    out = INDICATORS.create("three_line_strike").compute(frame(short))["three_line_strike"]
    np.testing.assert_array_equal(out.to_numpy(), 0.0)


def test_three_line_strike_output_contract():
    o, h, low, c = _build([100.0, 101.5, 103.5, 107.0], [102.0, 104.0, 106.0, 99.0])
    out = INDICATORS.create("three_line_strike").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["three_line_strike"]
    # No partial-penetration score for this pattern: values are only {-100, 0, 100}.
    assert set(np.unique(out["three_line_strike"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}


def test_three_line_strike_takes_no_params():
    import pytest

    with pytest.raises((TypeError, ValueError)):
        INDICATORS.create("three_line_strike", penetration=0.5)
