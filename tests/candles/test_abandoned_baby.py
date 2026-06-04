"""Abandoned Baby — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.abandoned_baby import abandoned_baby  # noqa: F401  (fires @register)

# 10 warm-up bars (body 1.0, HighLow 1.4) so BodyLong/BodyDoji averages are defined by the
# time the pattern forms at bars 10 -> 11 -> 12 (TA-Lib lookback is 12).
_WARM = 10
_WO = [100.0] * _WARM
_WC = [101.0] * _WARM
_WH = [101.2] * _WARM
_WL = [99.8] * _WARM


def _ab(o, h, low, c, **params):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("abandoned_baby", **params).compute(df)["abandoned_baby"].to_numpy()


def test_abandoned_baby_bullish():
    # Long black #1 (110->100), doji #2 gapped below, long white #3 gapped above closing deep
    # into #1's body (close 106 > 100 + 10*0.3 = 103) -> +100.
    o = _WO + [110.0, 95.0, 96.0]
    c = _WC + [100.0, 95.05, 106.0]
    h = _WH + [110.2, 95.3, 106.2]
    low = _WL + [99.8, 94.7, 95.8]
    assert _ab(o, h, low, c)[12] == 100.0


def test_abandoned_baby_bearish():
    # Long white #1 (100->110), doji #2 gapped above, long black #3 gapped below closing deep
    # into #1's body (close 106 < 110 - 10*0.3 = 107) -> -100.
    o = _WO + [100.0, 115.0, 114.0]
    c = _WC + [110.0, 115.05, 106.0]
    h = _WH + [110.2, 115.3, 114.2]
    low = _WL + [99.8, 114.7, 105.8]
    assert _ab(o, h, low, c)[12] == -100.0


def test_abandoned_baby_no_gap_is_zero():
    # Same as bullish but the doji's high touches #1's low (no downside gap) -> no pattern.
    o = _WO + [110.0, 95.0, 96.0]
    c = _WC + [100.0, 95.05, 106.0]
    h = _WH + [110.2, 99.9, 106.2]  # high[11]=99.9 > low[10]=99.8 -> no gap
    low = _WL + [99.8, 94.7, 95.8]
    assert _ab(o, h, low, c)[12] == 0.0


def test_abandoned_baby_shallow_close_is_zero():
    # Bullish geometry but #3 closes only to 102 (< 100 + 10*0.3 = 103) -> not deep enough.
    o = _WO + [110.0, 95.0, 96.0]
    c = _WC + [100.0, 95.05, 102.0]
    h = _WH + [110.2, 95.3, 102.2]
    low = _WL + [99.8, 94.7, 95.8]
    assert _ab(o, h, low, c)[12] == 0.0


def test_abandoned_baby_penetration_param():
    # The shallow close (102) becomes a signal once penetration drops to 0.1 (100+1=101 < 102).
    o = _WO + [110.0, 95.0, 96.0]
    c = _WC + [100.0, 95.05, 102.0]
    h = _WH + [110.2, 95.3, 102.2]
    low = _WL + [99.8, 94.7, 95.8]
    assert _ab(o, h, low, c, penetration=0.1)[12] == 100.0
    assert _ab(o, h, low, c, penetration=0.5)[12] == 0.0


def test_abandoned_baby_constant_frame_is_zero():
    # A flat (doji-everywhere) frame has no long bodies and no gaps -> all zeros.
    flat = [100.0] * 30
    out = _ab(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_abandoned_baby_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros, no IndexError.
    o = [100.0, 110.0, 95.0]
    c = [101.0, 100.0, 95.05]
    h = [101.2, 110.2, 95.3]
    low = [99.8, 99.8, 94.7]
    np.testing.assert_array_equal(_ab(o, h, low, c), 0.0)


def test_abandoned_baby_warmup_is_zero():
    o = _WO + [110.0, 95.0, 96.0]
    c = _WC + [100.0, 95.05, 106.0]
    h = _WH + [110.2, 95.3, 106.2]
    low = _WL + [99.8, 94.7, 95.8]
    np.testing.assert_array_equal(_ab(o, h, low, c)[:12], 0.0)  # TA-Lib lookback = 12


def test_abandoned_baby_output_contract():
    o = _WO + [110.0, 95.0, 96.0]
    c = _WC + [100.0, 95.05, 106.0]
    h = _WH + [110.2, 95.3, 106.2]
    low = _WL + [99.8, 94.7, 95.8]
    out = INDICATORS.create("abandoned_baby").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["abandoned_baby"]
    assert set(np.unique(out["abandoned_baby"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
