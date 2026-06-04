"""Evening Star — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.evening_star import evening_star  # noqa: F401  (import fires @register)

# 12 warm-up white bars (body 100->102) so the BodyLong/BodyShort averages are ~2.0 by the time
# the pattern can first form (third bar at index 14; TA-Lib lookback = 12).
_WARM = 12
_WO = [100.0] * _WARM
_WC = [102.0] * _WARM
_WH = [102.5] * _WARM
_WL = [99.5] * _WARM


def _evening_star(o, h, low, c, **kw):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("evening_star", **kw).compute(df)["evening_star"].to_numpy()


def _canonical():
    # 1st (idx12): long WHITE 100->110 (body 100..110, rb=10).
    # 2nd (idx13): short star gapping up, body 113..113.5 (bottom 113 > 1st top 110).
    # 3rd (idx14): BLACK 111->102.5; close 102.5 < 110 - 10*0.3 = 107 -> -100.
    o = _WO + [100.0, 113.0, 111.0]
    h = _WH + [110.5, 114.0, 111.2]
    low = _WL + [99.5, 112.5, 102.0]
    c = _WC + [110.0, 113.5, 102.5]
    return o, h, low, c


def test_evening_star_bearish_strict():
    assert _evening_star(*_canonical())[14] == -100.0


def test_evening_star_no_gap_is_zero():
    # 2nd body bottom merely touches the 1st body top (110): the gap-up is strict -> 0.
    o = _WO + [100.0, 110.0, 111.0]
    h = _WH + [110.5, 114.0, 111.2]
    low = _WL + [99.5, 109.5, 102.0]
    c = _WC + [110.0, 113.5, 102.5]
    assert _evening_star(o, h, low, c)[14] == 0.0


def test_evening_star_third_not_black_is_zero():
    # Make the 3rd candle white (close above open): not the closing black candle -> 0.
    o = _WO + [100.0, 113.0, 102.0]
    h = _WH + [110.5, 114.0, 111.2]
    low = _WL + [99.5, 112.5, 101.5]
    c = _WC + [110.0, 113.5, 111.0]
    assert _evening_star(o, h, low, c)[14] == 0.0


def test_evening_star_shallow_close_is_zero():
    # 3rd closes only just below the 1st close (108 > 110 - 10*0.3 = 107): not deep enough -> 0.
    o = _WO + [100.0, 113.0, 111.0]
    h = _WH + [110.5, 114.0, 111.2]
    low = _WL + [99.5, 112.5, 107.5]
    c = _WC + [110.0, 113.5, 108.0]
    assert _evening_star(o, h, low, c)[14] == 0.0


def test_evening_star_penetration_threshold():
    # Close at 108: zero at the default 0.3 (needs < 107) but fires at 0.5 (needs < 105)? No —
    # 108 > 105 too. Use a deeper penetration that *relaxes* the bar: pen=0.1 needs < 109, so
    # the same 108 close now qualifies. The param must thread through.
    o = _WO + [100.0, 113.0, 111.0]
    h = _WH + [110.5, 114.0, 111.2]
    low = _WL + [99.5, 112.5, 107.5]
    c = _WC + [110.0, 113.5, 108.0]
    assert _evening_star(o, h, low, c, penetration=0.3)[14] == 0.0
    assert _evening_star(o, h, low, c, penetration=0.1)[14] == -100.0


def test_evening_star_constant_frame_is_zero():
    # A flat frame (all bars identical, zero bodies) never forms the pattern.
    flat = [100.0] * 30
    np.testing.assert_array_equal(_evening_star(flat, flat, flat, flat), 0.0)


def test_evening_star_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (no room for the pattern).
    o = [100.0, 113.0, 111.0]
    h = [110.5, 114.0, 111.2]
    low = [99.5, 112.5, 102.0]
    c = [110.0, 113.5, 102.5]
    np.testing.assert_array_equal(_evening_star(o, h, low, c), 0.0)


def test_evening_star_warmup_is_zero():
    o, h, low, c = _canonical()
    np.testing.assert_array_equal(_evening_star(o, h, low, c)[:12], 0.0)  # TA-Lib lookback = 12


def test_evening_star_output_contract():
    o, h, low, c = _canonical()
    out = INDICATORS.create("evening_star").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["evening_star"]
    assert set(np.unique(out["evening_star"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}


def test_evening_star_rejects_unknown_param():
    with pytest.raises(Exception):  # noqa: B017,PT011  (pydantic extra='forbid')
        INDICATORS.create("evening_star", bogus=1)
