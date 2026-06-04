"""Three Stars In The South — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS

# import fires @register
from pyindicators.candles.three_stars_in_south import three_stars_in_south  # noqa: F401

# 12 warm-up bars with a moderate range (high-low = 6, body 0) so the 10-bar BodyLong/BodyShort
# and ShadowVeryShort averages are well defined by the time the pattern forms at bars 12->14.
_WARM = 12
_WO = [50.0] * _WARM
_WC = [50.0] * _WARM
_WH = [53.0] * _WARM
_WL = [47.0] * _WARM

# The three-bar pattern (bars 12, 13, 14):
#   1st: long black body (open 80 -> close 50, body 30) with a long lower shadow (low 19).
#   2nd: smaller black body (open 65 -> close 50, body 15) opening into the 1st range, higher
#        low (low 30 >= 19, < close[1st]=50), with a lower shadow.
#   3rd: small black marubozu (open 50.5 -> close 50) engulfed by the 2nd bar (low 49.9 > 30,
#        high 50.55 < 65.1), tiny shadows.
_PO = [80.0, 65.0, 50.5]
_PC = [50.0, 50.0, 50.0]
_PH = [80.1, 65.1, 50.55]
_PL = [19.0, 30.0, 49.9]


def _tsis(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("three_stars_in_south").compute(df)["three_stars_in_south"].to_numpy()


def _pattern_frame():
    return _WO + _PO, _WH + _PH, _WL + _PL, _WC + _PC


def test_three_stars_in_south_golden_hit():
    o, h, low, c = _pattern_frame()
    out = _tsis(o, h, low, c)
    assert out[14] == 100.0  # the pattern completes on the third bar


def test_three_stars_in_south_warmup_is_zero():
    o, h, low, c = _pattern_frame()
    np.testing.assert_array_equal(_tsis(o, h, low, c)[:12], 0.0)  # TA-Lib lookback = 12


def test_three_stars_in_south_first_must_be_black():
    # Make the 1st pattern bar white (close > open) -> no pattern.
    o, h, low, c = _pattern_frame()
    o[12], c[12] = 50.0, 80.0  # white long body
    assert _tsis(o, h, low, c)[14] == 0.0


def test_three_stars_in_south_third_must_be_inside():
    # Push the 3rd bar's low below the 2nd bar's low -> engulfing fails.
    o, h, low, c = _pattern_frame()
    low[14] = 29.0  # below 2nd bar low (30)
    assert _tsis(o, h, low, c)[14] == 0.0


def test_three_stars_in_south_constant_frame_is_zero():
    # A flat OHLC frame has no bodies/shadows and can never form the pattern.
    n = 40
    out = _tsis([10.0] * n, [10.0] * n, [10.0] * n, [10.0] * n)
    np.testing.assert_array_equal(out, 0.0)


def test_three_stars_in_south_short_frame_is_zero():
    # Frames at or below the 12-bar lookback are all zero.
    for n in (1, 3, 12, 13):
        c = [50.0, 49.0] * n
        c = c[:n]
        out = _tsis([51.0] * n, [52.0] * n, [40.0] * n, c)
        assert out.shape == (n,)
        np.testing.assert_array_equal(out[: min(n, 12)], 0.0)


def test_three_stars_in_south_output_contract():
    o, h, low, c = _pattern_frame()
    out = INDICATORS.create("three_stars_in_south").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["three_stars_in_south"]
    vals = set(np.unique(out["three_stars_in_south"].to_numpy()))
    assert vals <= {-100.0, -80.0, 0.0, 80.0, 100.0}
