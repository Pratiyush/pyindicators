"""Inverted Hammer — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.inverted_hammer import inverted_hammer  # noqa: F401  (fires @register)

# 11 warm-up bars (body 1.0, high-low 2.0) -> BodyShort avg = 1.0, ShadowVeryShort avg = 0.2.
# Bar 11 is a normal "prior" bar whose real body spans [100, 101] (min(o,c) = 100).
# Bar 12 is an inverted hammer that gaps DOWN below it: tiny body near the low, long upper
#   shadow, no lower shadow, with max(o,c) = 90.10 < 100. -> fires (+100).
# Bar 13 has the same shape but NO gap (body back up at ~100), so the gap-down clause fails -> 0.
_WARM = 11
_OPEN = [100.0] * _WARM + [100.0, 90.10, 100.10]
_CLOSE = [101.0] * _WARM + [101.0, 90.00, 100.00]
_HIGH = [101.5] * _WARM + [101.5, 92.00, 102.00]
_LOW = [99.5] * _WARM + [99.5, 90.00, 100.00]


def _ih(df):
    return INDICATORS.create("inverted_hammer").compute(df)["inverted_hammer"].to_numpy()


def test_inverted_hammer_golden_hit_and_miss():
    out = _ih(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[12] == 100.0  # tiny body, long upper shadow, no lower shadow, gaps down below prior
    assert out[13] == 0.0  # identical shape but no gap-down -> not an inverted hammer


def test_inverted_hammer_warmup_is_zero():
    out = _ih(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    np.testing.assert_array_equal(out[:11], 0.0)  # TA-Lib lookback = 11 (BodyShort 10 + 1 prior)


def test_inverted_hammer_constant_frame_is_zero():
    # A flat frame (open == high == low == close) has no body and no shadows -> never fires.
    c = [50.0] * 40
    out = _ih(frame(c, high=c, low=c, open_=c))
    np.testing.assert_array_equal(out, 0.0)


def test_inverted_hammer_short_frame_is_zero():
    # Fewer bars than the lookback -> every bar is inside the warm-up -> all zeros.
    c = [100.0, 101.0, 99.0, 102.0, 98.0]
    out = _ih(frame(c, high=[x + 1 for x in c], low=[x - 1 for x in c], open_=c))
    np.testing.assert_array_equal(out, 0.0)


def test_inverted_hammer_output_contract():
    out = INDICATORS.create("inverted_hammer").compute(
        frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN)
    )
    assert list(out.columns) == ["inverted_hammer"]
    assert set(np.unique(out["inverted_hammer"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
