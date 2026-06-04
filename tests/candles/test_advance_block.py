"""Advance Block — golden + edge cases (deterministic; no reference library).

CDLADVANCEBLOCK is bearish-only: TA-Lib emits 0 or -100 (no +100, no partial ±80 score).
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.advance_block import advance_block  # noqa: F401  (import fires @register)

# 12 warm-up white bars (small body 0.5, upper/lower shadow 0.1) so the BodyLong/ShadowShort/
# Near/Far averages are small by the time the pattern forms across bars 12->13->14.
_WARM = 12
_WO = [100.0] * _WARM
_WC = [100.5] * _WARM
_WH = [100.6] * _WARM
_WL = [99.9] * _WARM


def _ab(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("advance_block").compute(df)["advance_block"].to_numpy()


def test_advance_block_trigger_is_minus_100():
    # Three white candles, higher closes, each opening inside the prior body; first body long
    # with a flat top (upper shadow 0); bodies shrink 10 -> 9 -> 7 and the 2nd/3rd grow long
    # upper shadows -> a deteriorating advance -> -100.
    o = _WO + [100.0, 104.0, 108.0]
    c = _WC + [110.0, 113.0, 115.0]
    h = _WH + [110.0, 116.0, 119.0]
    low = _WL + [99.9, 103.9, 107.9]
    assert _ab(o, h, low, c)[14] == -100.0


def test_advance_block_growing_bodies_is_zero():
    # Three white candles advancing but with *growing* bodies and short shadows -> no
    # deterioration -> not an advance block -> 0.
    o = _WO + [100.0, 101.0, 102.0]
    c = _WC + [105.0, 107.0, 110.0]
    h = _WH + [105.0, 107.0, 110.0]
    low = _WL + [99.9, 100.9, 101.9]
    assert _ab(o, h, low, c)[14] == 0.0


def test_advance_block_constant_frame_is_zero():
    # A flat (doji) constant series can never satisfy the white/long-body conditions -> all 0.
    n = 40
    flat = [100.0] * n
    out = _ab(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, np.zeros(n))


def test_advance_block_short_frame_is_zero():
    # Fewer bars than the 12-bar lookback -> all 0 (no room for the averages or the window).
    o = [100.0, 101.0, 102.0, 103.0, 104.0]
    c = [101.0, 102.0, 103.0, 104.0, 105.0]
    h = [101.5, 102.5, 103.5, 104.5, 105.5]
    low = [99.5, 100.5, 101.5, 102.5, 103.5]
    np.testing.assert_array_equal(_ab(o, h, low, c), np.zeros(5))


def test_advance_block_warmup_is_zero():
    o = _WO + [100.0, 104.0, 108.0]
    c = _WC + [110.0, 113.0, 115.0]
    h = _WH + [110.0, 116.0, 119.0]
    low = _WL + [99.9, 103.9, 107.9]
    np.testing.assert_array_equal(_ab(o, h, low, c)[:12], 0.0)  # TA-Lib lookback = 12


def test_advance_block_output_contract():
    o = _WO + [100.0, 104.0, 108.0]
    c = _WC + [110.0, 113.0, 115.0]
    h = _WH + [110.0, 116.0, 119.0]
    low = _WL + [99.9, 103.9, 107.9]
    out = INDICATORS.create("advance_block").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["advance_block"]
    assert set(np.unique(out["advance_block"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
