"""Stalled Pattern — golden + edge cases (deterministic; no reference library).

CDLSTALLEDPATTERN is bearish-only: TA-Lib emits 0 or -100 (no +100, no partial ±80 score).
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.stalled_pattern import stalled_pattern  # noqa: F401  (fires @register)

# 12 warm-up white bars with small bodies/shadows so the BodyLong/BodyShort/ShadowVeryShort/
# Near averages stay tiny by the time the pattern forms across bars 12 -> 13 -> 14.
_WARM = 12
_WO = [100.0] * _WARM
_WC = [100.3] * _WARM
_WH = [100.35] * _WARM
_WL = [99.95] * _WARM


def _sp(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("stalled_pattern").compute(df)["stalled_pattern"].to_numpy()


def test_stalled_trigger_is_minus_100():
    # Three white candles with higher closes: 1st & 2nd long-bodied, the 2nd with a very short
    # upper shadow opening within the 1st body, and a small 3rd body riding the 2nd's shoulder
    # -> the advance stalls -> -100.
    o = _WO + [100.0, 105.0, 119.6]
    c = _WC + [110.0, 119.0, 119.8]
    h = _WH + [110.0, 119.05, 119.9]
    low = _WL + [99.9, 104.9, 119.5]
    assert _sp(o, h, low, c)[14] == -100.0


def test_stalled_growing_third_body_is_zero():
    # Same first two bars, but the 3rd has a large (not small) real body -> the advance is not
    # stalling -> not a stalled pattern -> 0.
    o = _WO + [100.0, 105.0, 112.0]
    c = _WC + [110.0, 119.0, 125.0]
    h = _WH + [110.0, 119.05, 125.0]
    low = _WL + [99.9, 104.9, 111.9]
    assert _sp(o, h, low, c)[14] == 0.0


def test_stalled_constant_frame_is_zero():
    # A flat (doji) constant series can never satisfy the white/long-body conditions -> all 0.
    n = 40
    flat = [100.0] * n
    out = _sp(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, np.zeros(n))


def test_stalled_short_frame_is_zero():
    # Fewer bars than the 12-bar lookback -> all 0 (no room for the averages or the window).
    o = [100.0, 101.0, 102.0, 103.0, 104.0]
    c = [101.0, 102.0, 103.0, 104.0, 105.0]
    h = [101.5, 102.5, 103.5, 104.5, 105.5]
    low = [99.5, 100.5, 101.5, 102.5, 103.5]
    np.testing.assert_array_equal(_sp(o, h, low, c), np.zeros(5))


def test_stalled_warmup_is_zero():
    o = _WO + [100.0, 105.0, 119.6]
    c = _WC + [110.0, 119.0, 119.8]
    h = _WH + [110.0, 119.05, 119.9]
    low = _WL + [99.9, 104.9, 119.5]
    np.testing.assert_array_equal(_sp(o, h, low, c)[:12], 0.0)  # TA-Lib lookback = 12


def test_stalled_output_contract():
    o = _WO + [100.0, 105.0, 119.6]
    c = _WC + [110.0, 119.0, 119.8]
    h = _WH + [110.0, 119.05, 119.9]
    low = _WL + [99.9, 104.9, 119.5]
    out = INDICATORS.create("stalled_pattern").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["stalled_pattern"]
    assert set(np.unique(out["stalled_pattern"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
