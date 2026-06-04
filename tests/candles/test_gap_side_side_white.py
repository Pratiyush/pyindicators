"""Gap side-by-side white lines — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.candles.gap_side_side_white import (  # noqa: F401  (import fires @register)
    gap_side_side_white,
)

# 7 flat warm-up bars (small doji-ish range) so the Near/Equal HighLow averages are well defined
# and tiny by the time the pattern forms at the gap candle (bar 7) -> first/second whites.
_WARM = 7
_WO = [50.0] * _WARM
_WC = [50.0] * _WARM
_WH = [50.1] * _WARM
_WL = [49.9] * _WARM


def _gssw(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("gap_side_side_white").compute(df)["gap_side_side_white"].to_numpy()


def test_gap_side_side_white_upside_gap_is_100():
    # Pre-gap candle (bar 7) tops out near 50; two identical white candles gap up above it and
    # open at the same level with the same body size -> +100 at the second white (bar 9).
    o = _WO + [50.0, 60.0, 60.0]
    c = _WC + [50.0, 62.0, 62.0]
    h = _WH + [50.1, 62.1, 62.1]
    low = _WL + [49.9, 59.9, 59.9]
    out = _gssw(o, h, low, c)
    assert out[9] == 100.0


def test_gap_side_side_white_downside_gap_is_minus_100():
    # Two identical white candles gap *down* below the pre-gap candle -> -100 (bearish gap).
    o = _WO + [50.0, 40.0, 40.0]
    c = _WC + [50.0, 42.0, 42.0]
    h = _WH + [50.1, 42.1, 42.1]
    low = _WL + [49.9, 39.9, 39.9]
    out = _gssw(o, h, low, c)
    assert out[9] == -100.0


def test_gap_side_side_white_no_gap_is_zero():
    # Two identical white bodies but overlapping the pre-gap body (no gap) -> 0.
    o = _WO + [50.0, 50.0, 50.0]
    c = _WC + [52.0, 52.0, 52.0]
    h = _WH + [52.1, 52.1, 52.1]
    low = _WL + [49.9, 49.9, 49.9]
    out = _gssw(o, h, low, c)
    assert out[9] == 0.0


def test_gap_side_side_white_second_black_is_zero():
    # Upside gap but the second candle is black (close < open) -> not the pattern -> 0.
    o = _WO + [50.0, 60.0, 62.0]
    c = _WC + [50.0, 62.0, 60.0]
    h = _WH + [50.1, 62.1, 62.1]
    low = _WL + [49.9, 59.9, 59.9]
    out = _gssw(o, h, low, c)
    assert out[9] == 0.0


def test_gap_side_side_white_constant_frame_is_zero():
    # A perfectly flat frame has no bodies and no gaps anywhere -> all zeros.
    out = _gssw([50.0] * 30, [50.0] * 30, [50.0] * 30, [50.0] * 30)
    np.testing.assert_array_equal(out, 0.0)


def test_gap_side_side_white_short_frame_is_zero():
    # Fewer bars than the lookback (7) -> everything is 0.
    o = [50.0, 51.0, 52.0, 53.0, 54.0]
    out = _gssw(o, [x + 0.1 for x in o], [x - 0.1 for x in o], o)
    np.testing.assert_array_equal(out, 0.0)


def test_gap_side_side_white_warmup_is_zero():
    o = _WO + [50.0, 60.0, 60.0]
    c = _WC + [50.0, 62.0, 62.0]
    h = _WH + [50.1, 62.1, 62.1]
    low = _WL + [49.9, 59.9, 59.9]
    np.testing.assert_array_equal(_gssw(o, h, low, c)[:7], 0.0)  # TA-Lib lookback = 7


def test_gap_side_side_white_output_contract():
    df = deterministic_frame()
    out = INDICATORS.create("gap_side_side_white").compute(df)
    assert list(out.columns) == ["gap_side_side_white"]
    uniq = set(np.unique(out["gap_side_side_white"].to_numpy()))
    assert uniq <= {-100.0, -80.0, 0.0, 80.0, 100.0}
