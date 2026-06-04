"""On-Neck — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.on_neck import on_neck  # noqa: F401  (import fires @register)

# 11 warm-up bars with body 9.0 (109 -> 100) so the BodyLong average settles at 9.0 and a
# body-10.0 bar at index 11 counts as "long". Small ranges keep the Equal band wide enough
# that a close *at* the prior low lands inside it.
_WARM = 11
_WO = [109.0] * _WARM
_WC = [100.0] * _WARM
_WH = [109.3] * _WARM
_WL = [99.7] * _WARM


def _on(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("on_neck").compute(df)["on_neck"].to_numpy()


def test_on_neck_bearish_hit():
    # Long black (110->100, low 99.5) then a white bar gapping down (open 98) that closes
    # right at the prior low (99.5) -> bearish continuation -100.
    o = _WO + [110.0, 98.0]
    c = _WC + [100.0, 99.5]
    h = _WH + [110.5, 99.6]
    low = _WL + [99.5, 97.5]
    assert _on(o, h, low, c)[12] == -100.0


def test_on_neck_close_above_band_is_zero():
    # Second bar closes well above the prior low (outside the Equal band) -> not On-Neck.
    o = _WO + [110.0, 98.0]
    c = _WC + [100.0, 101.0]
    h = _WH + [110.5, 101.1]
    low = _WL + [99.5, 97.5]
    assert _on(o, h, low, c)[12] == 0.0


def test_on_neck_open_not_below_prior_low_is_zero():
    # Second bar does not gap below the prior low (open 100 > low 99.5) -> not On-Neck.
    o = _WO + [110.0, 100.0]
    c = _WC + [100.0, 99.5]
    h = _WH + [110.5, 100.5]
    low = _WL + [99.5, 99.0]
    assert _on(o, h, low, c)[12] == 0.0


def test_on_neck_prior_body_not_long_is_zero():
    # First bar's body (8.0) is below the BodyLong average (9.0) -> not a long black bar.
    o = _WO + [108.0, 98.0]
    c = _WC + [100.0, 99.5]
    h = _WH + [108.3, 99.6]
    low = _WL + [99.5, 97.5]
    assert _on(o, h, low, c)[12] == 0.0


def test_on_neck_constant_frame_is_zero():
    # A flat frame (open == close, zero range) can never form the pattern.
    flat = [100.0] * 20
    out = _on(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_on_neck_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (no warm-up completed).
    o = [109.0, 110.0, 98.0]
    c = [100.0, 100.0, 99.5]
    h = [109.3, 110.5, 99.6]
    low = [99.7, 99.5, 97.5]
    np.testing.assert_array_equal(_on(o, h, low, c), 0.0)


def test_on_neck_warmup_is_zero():
    o = _WO + [110.0, 98.0]
    c = _WC + [100.0, 99.5]
    h = _WH + [110.5, 99.6]
    low = _WL + [99.5, 97.5]
    np.testing.assert_array_equal(_on(o, h, low, c)[:11], 0.0)  # TA-Lib lookback = 11


def test_on_neck_output_contract():
    o = _WO + [110.0, 98.0]
    c = _WC + [100.0, 99.5]
    h = _WH + [110.5, 99.6]
    low = _WL + [99.5, 97.5]
    out = INDICATORS.create("on_neck").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["on_neck"]
    assert set(np.unique(out["on_neck"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
