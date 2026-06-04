"""Three Inside Up/Down — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.three_inside import three_inside  # noqa: F401  (import fires @register)

# 12 warm-up bars (body 2.0) so BodyLong/BodyShort averages are 2.0 by the time the pattern
# can form at bar 12 (1st), 13 (2nd), 14 (3rd).
_WARM = 12
_WO = [100.0] * _WARM
_WC = [102.0] * _WARM
_WH = [102.2] * _WARM
_WL = [99.8] * _WARM


def _ti(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("three_inside").compute(df)["three_inside"].to_numpy()


def test_three_inside_up_is_plus_100():
    # 1st long black (110->100); 2nd small white strictly inside; 3rd white closing above the
    # 1st open (110) -> Three Inside Up = +100.
    o = _WO + [110.0, 102.0, 101.0]
    c = _WC + [100.0, 103.0, 111.0]
    h = _WH + [110.5, 103.5, 111.5]
    low = _WL + [99.5, 101.5, 100.5]
    assert _ti(o, h, low, c)[14] == 100.0


def test_three_inside_down_is_minus_100():
    # 1st long white (100->110); 2nd small black strictly inside; 3rd black closing below the
    # 1st open (100) -> Three Inside Down = -100.
    o = _WO + [100.0, 108.0, 109.0]
    c = _WC + [110.0, 107.0, 99.0]
    h = _WH + [110.5, 108.5, 109.5]
    low = _WL + [99.5, 106.5, 98.5]
    assert _ti(o, h, low, c)[14] == -100.0


def test_three_inside_third_wrong_direction_is_zero():
    # Valid harami (long black, short white inside) but the 3rd candle does NOT close above
    # the 1st open (closes at 105 < 110) -> no confirmation -> 0.
    o = _WO + [110.0, 102.0, 101.0]
    c = _WC + [100.0, 103.0, 105.0]
    h = _WH + [110.5, 103.5, 105.5]
    low = _WL + [99.5, 101.5, 100.5]
    assert _ti(o, h, low, c)[14] == 0.0


def test_three_inside_second_not_inside_is_zero():
    # 2nd body is NOT engulfed by the 1st (its top 104 exceeds the 1st body top 110? no — make
    # the 2nd body break the 1st low instead: open 99 < 1st low edge 100) -> 0.
    o = _WO + [110.0, 99.0, 101.0]
    c = _WC + [100.0, 101.0, 111.0]
    h = _WH + [110.5, 101.5, 111.5]
    low = _WL + [99.5, 98.5, 100.5]
    assert _ti(o, h, low, c)[14] == 0.0


def test_three_inside_constant_frame_is_zero():
    # A flat doji-only frame (no real bodies) can never satisfy the long-1st-body test -> all 0.
    flat = [100.0] * 40
    out = _ti(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_three_inside_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (no pattern can clear the warm-up).
    o = [100.0, 110.0, 102.0]
    c = [100.0, 100.0, 103.0]
    h = [100.5, 110.5, 103.5]
    low = [99.5, 99.5, 101.5]
    out = _ti(o, h, low, c)
    np.testing.assert_array_equal(out, 0.0)


def test_three_inside_lookback_zeros_first_twelve():
    o = _WO + [110.0, 102.0, 101.0]
    c = _WC + [100.0, 103.0, 111.0]
    h = _WH + [110.5, 103.5, 111.5]
    low = _WL + [99.5, 101.5, 100.5]
    np.testing.assert_array_equal(_ti(o, h, low, c)[:12], 0.0)  # TA-Lib lookback = 12


def test_three_inside_output_contract():
    o = _WO + [110.0, 102.0, 101.0]
    c = _WC + [100.0, 103.0, 111.0]
    h = _WH + [110.5, 103.5, 111.5]
    low = _WL + [99.5, 101.5, 100.5]
    out = INDICATORS.create("three_inside").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["three_inside"]
    assert set(np.unique(out["three_inside"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
