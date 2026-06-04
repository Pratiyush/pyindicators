"""Tristar — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.tristar import tristar  # noqa: F401  (import fires @register)

# 10 warm-up bars with a high-low range of 20 -> BodyDoji average = 0.1 * 20 = 2.0, so any
# body below 2.0 counts as a doji by the time the pattern can form at bar 12.
_WARM = 10
_WO = [100.0] * _WARM
_WC = [100.0] * _WARM
_WH = [110.0] * _WARM
_WL = [90.0] * _WARM


def _tri(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("tristar").compute(df)["tristar"].to_numpy()


def test_tristar_bullish_gap_down():
    # 1st doji ~100, 2nd doji gaps DOWN to ~90, 3rd doji low (89.5) > 2nd low (89.0) -> +100.
    o = _WO + [100.0, 90.0, 92.0]
    c = _WC + [100.5, 90.5, 92.3]
    h = _WH + [101.0, 91.0, 93.0]
    low = _WL + [99.5, 89.0, 89.5]
    assert _tri(o, h, low, c)[12] == 100.0


def test_tristar_bearish_gap_up():
    # 1st doji ~100, 2nd doji gaps UP to ~110, 3rd doji high (109.0) < 2nd high (111.5) -> -100.
    o = _WO + [100.0, 110.0, 108.0]
    c = _WC + [100.5, 110.5, 108.3]
    h = _WH + [101.0, 111.5, 109.0]
    low = _WL + [99.5, 109.0, 107.0]
    assert _tri(o, h, low, c)[12] == -100.0


def test_tristar_no_gap_is_zero():
    # Three dojis but the middle body overlaps the first (no gap) -> 0.
    o = _WO + [100.0, 100.2, 100.1]
    c = _WC + [100.5, 100.6, 100.4]
    h = _WH + [101.0, 101.0, 101.0]
    low = _WL + [99.5, 99.6, 99.4]
    assert _tri(o, h, low, c)[12] == 0.0


def test_tristar_third_extends_gap_is_zero():
    # Bearish geometry but the 3rd high (112.0) is NOT below the 2nd high (111.5) -> 0.
    o = _WO + [100.0, 110.0, 110.5]
    c = _WC + [100.5, 110.5, 111.0]
    h = _WH + [101.0, 111.5, 112.0]
    low = _WL + [99.5, 109.0, 109.5]
    assert _tri(o, h, low, c)[12] == 0.0


def test_tristar_big_middle_body_is_not_doji():
    # The middle bar gaps up but has a large body (12 > 2.0 average) so it is not a doji -> 0.
    o = _WO + [100.0, 110.0, 108.0]
    c = _WC + [100.5, 122.0, 108.3]
    h = _WH + [101.0, 123.0, 109.0]
    low = _WL + [99.5, 109.0, 107.0]
    assert _tri(o, h, low, c)[12] == 0.0


def test_tristar_constant_frame_is_zero():
    # A perfectly flat frame: every body is a doji, but there is never a gap -> all zeros.
    n = 40
    out = _tri([100.0] * n, [101.0] * n, [99.0] * n, [100.0] * n)
    np.testing.assert_array_equal(out, 0.0)


def test_tristar_warmup_is_zero():
    o = _WO + [100.0, 90.0, 92.0]
    c = _WC + [100.5, 90.5, 92.3]
    h = _WH + [101.0, 91.0, 93.0]
    low = _WL + [99.5, 89.0, 89.5]
    np.testing.assert_array_equal(_tri(o, h, low, c)[:12], 0.0)  # TA-Lib lookback = 12


def test_tristar_short_frame_is_zero():
    # Fewer than (lookback + 1) bars -> nothing can fire.
    out = _tri([100.0] * 12, [101.0] * 12, [99.0] * 12, [100.0] * 12)
    assert out.shape == (12,)
    np.testing.assert_array_equal(out, 0.0)


def test_tristar_output_contract():
    o = _WO + [100.0, 90.0, 92.0]
    c = _WC + [100.5, 90.5, 92.3]
    h = _WH + [101.0, 91.0, 93.0]
    low = _WL + [99.5, 89.0, 89.5]
    out = INDICATORS.create("tristar").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["tristar"]
    assert set(np.unique(out["tristar"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
