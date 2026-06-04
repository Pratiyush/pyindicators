"""Morning Star — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.morning_star import morning_star  # noqa: F401  (import fires @register)

# 12 warm-up black bars (body 102->100) so the BodyLong/BodyShort averages are ~2.0 by the time
# the pattern can first form (third bar at index 14; TA-Lib lookback = 12).
_WARM = 12
_WO = [102.0] * _WARM
_WC = [100.0] * _WARM
_WH = [102.5] * _WARM
_WL = [99.5] * _WARM


def _morning_star(o, h, low, c, **kw):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("morning_star", **kw).compute(df)["morning_star"].to_numpy()


def _canonical():
    # 1st (idx12): long BLACK 110->100 (body 100..110, rb=10).
    # 2nd (idx13): short star gapping down, body 96..96.5 (top 96.5 < 1st bottom 100).
    # 3rd (idx14): WHITE 98->107.5; close 107.5 > 100 + 10*0.3 = 103 -> +100.
    o = _WO + [110.0, 96.5, 98.0]
    h = _WH + [110.5, 97.0, 107.8]
    low = _WL + [99.5, 96.0, 97.5]
    c = _WC + [100.0, 96.0, 107.5]
    return o, h, low, c


def test_morning_star_bullish_strict():
    assert _morning_star(*_canonical())[14] == 100.0


def test_morning_star_no_gap_is_zero():
    # 2nd body top merely touches the 1st body bottom (100): the gap-down is strict -> 0.
    o = _WO + [110.0, 100.0, 98.0]
    h = _WH + [110.5, 100.5, 107.8]
    low = _WL + [99.5, 96.0, 97.5]
    c = _WC + [100.0, 96.0, 107.5]
    assert _morning_star(o, h, low, c)[14] == 0.0


def test_morning_star_third_not_white_is_zero():
    # Make the 3rd candle black (close below open): not the closing white candle -> 0.
    o = _WO + [110.0, 96.5, 108.0]
    h = _WH + [110.5, 97.0, 108.5]
    low = _WL + [99.5, 96.0, 98.5]
    c = _WC + [100.0, 96.0, 99.0]
    assert _morning_star(o, h, low, c)[14] == 0.0


def test_morning_star_shallow_close_is_zero():
    # 3rd closes only just above the 1st close (102 < 100 + 10*0.3 = 103): not deep enough -> 0.
    o = _WO + [110.0, 96.5, 98.0]
    h = _WH + [110.5, 97.0, 102.5]
    low = _WL + [99.5, 96.0, 97.5]
    c = _WC + [100.0, 96.0, 102.0]
    assert _morning_star(o, h, low, c)[14] == 0.0


def test_morning_star_penetration_threshold():
    # Close at 102: zero at the default 0.3 (needs > 103) but fires at 0.1 (needs > 101) — the
    # deeper-penetration (smaller fraction) relaxes the bar. The param must thread through.
    o = _WO + [110.0, 96.5, 98.0]
    h = _WH + [110.5, 97.0, 102.5]
    low = _WL + [99.5, 96.0, 97.5]
    c = _WC + [100.0, 96.0, 102.0]
    assert _morning_star(o, h, low, c, penetration=0.3)[14] == 0.0
    assert _morning_star(o, h, low, c, penetration=0.1)[14] == 100.0


def test_morning_star_constant_frame_is_zero():
    # A flat frame (all bars identical, zero bodies) never forms the pattern.
    flat = [100.0] * 30
    np.testing.assert_array_equal(_morning_star(flat, flat, flat, flat), 0.0)


def test_morning_star_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (no room for the pattern).
    o = [110.0, 96.5, 98.0]
    h = [110.5, 97.0, 107.8]
    low = [99.5, 96.0, 97.5]
    c = [100.0, 96.0, 107.5]
    np.testing.assert_array_equal(_morning_star(o, h, low, c), 0.0)


def test_morning_star_warmup_is_zero():
    o, h, low, c = _canonical()
    np.testing.assert_array_equal(_morning_star(o, h, low, c)[:12], 0.0)  # TA-Lib lookback = 12


def test_morning_star_output_contract():
    o, h, low, c = _canonical()
    out = INDICATORS.create("morning_star").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["morning_star"]
    assert set(np.unique(out["morning_star"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}


def test_morning_star_rejects_unknown_param():
    with pytest.raises(Exception):  # noqa: B017,PT011  (pydantic extra='forbid')
        INDICATORS.create("morning_star", bogus=1)
