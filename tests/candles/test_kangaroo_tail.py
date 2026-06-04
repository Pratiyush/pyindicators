"""Kangaroo Tail — golden + edge cases (deterministic; no reference library).

A Kangaroo Tail (Nial Fuller pin bar) fires ``-100`` for a long *upper* tail that pierces the
prior-``N`` rolling high but whose body closes back below it, and ``+100`` for the bullish
mirror against the prior-``N`` rolling low. The tail must be at least ``tail_mult``× both the
real body and the opposite wick. The first ``N`` bars are 0 (warm-up). These tests hand-build
OHLC bars so the prior high/low are known exactly, then assert the documented rule.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.kangaroo_tail import kangaroo_tail  # noqa: F401  (import fires @register)

_N = 5  # short window for compact golden frames


def _kt(o, h, low, c, length=_N, tail_mult=2.0):
    df = frame(c, high=h, low=low, open_=o)
    return (
        INDICATORS.create("kangaroo_tail", length=length, tail_mult=tail_mult)
        .compute(df)["kangaroo_tail"]
        .to_numpy()
    )


# A flat plateau of ``_N`` bars at H=11/L=9/O=C=10 makes prior_high = 11 and prior_low = 9 for
# the bar that immediately follows it, so the test bar's behaviour is fully determined.
_PH = [11.0] * _N
_PL = [9.0] * _N
_PC = [10.0] * _N
_PO = [10.0] * _N


def test_kangaroo_tail_bearish_golden_hit():
    # Test bar: body 10.0->10.2 (body 0.2), spikes to high 12.0 (> prior_high 11, upper tail
    # 12.0-10.2 = 1.8 >= 2*0.2 and >> 2*lower_tail), low 10.0 (lower tail 0.0). open 10.0 and
    # close 10.2 are both < prior_high 11 -> bearish kangaroo tail -100.
    o = _PO + [10.0]
    h = _PH + [12.0]
    low = _PL + [10.0]
    c = _PC + [10.2]
    assert _kt(o, h, low, c)[_N] == -100.0


def test_kangaroo_tail_bullish_golden_hit():
    # Mirror: body 10.0->9.8 (body 0.2), dips to low 8.0 (< prior_low 9, lower tail
    # 9.8-8.0 = 1.8), high 10.0 (upper tail 0.0). open 10.0 and close 9.8 both > prior_low 9
    # -> bullish kangaroo tail +100.
    o = _PO + [10.0]
    h = _PH + [10.0]
    low = _PL + [8.0]
    c = _PC + [9.8]
    assert _kt(o, h, low, c)[_N] == 100.0


def test_kangaroo_tail_short_tail_is_zero():
    # High pokes above prior_high (11.5 > 11) and closes back inside, but the upper tail
    # (11.5-10.5 = 1.0) is only 2*body (body 0.5) -> qualifies on body... make body bigger so
    # the tail is < 2*body: body 1.0 (10.0->11.0... but that would close above). Use a wide body
    # so tail < 2*body: open 9.5, close 10.8 (body 1.3), high 11.5 (upper tail 0.7 < 2*1.3).
    o = _PO + [9.5]
    h = _PH + [11.5]
    low = _PL + [9.5]
    c = _PC + [10.8]
    assert _kt(o, h, low, c)[_N] == 0.0


def test_kangaroo_tail_no_poke_is_zero():
    # Long upper tail and tiny body, but the high (10.9) never pierces prior_high (11) -> no
    # rejection of the range -> 0.
    o = _PO + [10.0]
    h = _PH + [10.9]
    low = _PL + [10.0]
    c = _PC + [10.1]
    assert _kt(o, h, low, c)[_N] == 0.0


def test_kangaroo_tail_close_above_prior_high_is_zero():
    # Long upper tail that pokes above prior_high (12 > 11), but the close (11.5) stays ABOVE
    # prior_high -> a genuine breakout, not a rejection -> 0.
    o = _PO + [10.0]
    h = _PH + [12.0]
    low = _PL + [10.0]
    c = _PC + [11.5]
    assert _kt(o, h, low, c)[_N] == 0.0


def test_kangaroo_tail_high_touches_prior_high_is_zero():
    # High touches prior_high exactly (11.0) without piercing it; the poke test is strict
    # (high > prior_high) -> 0.
    o = _PO + [10.0]
    h = _PH + [11.0]
    low = _PL + [10.0]
    c = _PC + [10.1]
    assert _kt(o, h, low, c)[_N] == 0.0


def test_kangaroo_tail_dominant_opposite_wick_is_zero():
    # Long upper tail that pokes and reclaims, but the LOWER wick is comparably long (both tails
    # ~1.8), so neither tail dominates -> not a one-sided pin -> 0.
    o = _PO + [10.0]
    h = _PH + [12.0]  # upper tail 12.0 - 10.0 = 2.0 (body top = 10.0, body 0)
    low = _PL + [8.0]  # lower tail 10.0 - 8.0 = 2.0
    c = _PC + [10.0]  # body 0
    assert _kt(o, h, low, c)[_N] == 0.0


def test_kangaroo_tail_constant_frame_is_zero():
    # A flat series (open == high == low == close) has prior_high == prior_low == price and zero
    # tails/body; strict poke comparisons never fire -> all 0.
    c = [10.0] * 30
    out = _kt(c, c, c, c)
    np.testing.assert_array_equal(out, 0.0)


def test_kangaroo_tail_warmup_is_zero():
    # The first ``length`` bars have no full prior window -> forced to 0.
    o = _PO + [10.0]
    h = _PH + [12.0]
    low = _PL + [10.0]
    c = _PC + [10.2]
    np.testing.assert_array_equal(_kt(o, h, low, c)[:_N], 0.0)


def test_kangaroo_tail_short_frame_is_zero():
    # Fewer bars than the window -> every output is 0.
    o = [10.0, 10.0, 10.0]
    h = [11.0, 12.0, 12.0]
    low = [9.0, 10.0, 10.0]
    c = [10.0, 10.2, 10.2]
    np.testing.assert_array_equal(_kt(o, h, low, c), 0.0)


def test_kangaroo_tail_output_contract():
    o = _PO + [10.0]
    h = _PH + [12.0]
    low = _PL + [10.0]
    c = _PC + [10.2]
    out = INDICATORS.create("kangaroo_tail", length=_N).compute(
        frame(c, high=h, low=low, open_=o)
    )
    assert list(out.columns) == ["kangaroo_tail"]
    assert str(out["kangaroo_tail"].dtype) == "float64"
    assert set(np.unique(out["kangaroo_tail"].to_numpy())) <= {-100.0, 0.0, 100.0}


def test_kangaroo_tail_default_length_is_20():
    # Default window is 20: a 21-bar frame has exactly one post-warm-up bar (index 20).
    n = 21
    high = [11.0] * n
    low = [9.0] * n
    close = [10.0] * n
    open_ = [10.0] * n
    high[-1] = 12.0  # final bar pierces prior_high 11 with a long upper tail
    close[-1] = 10.2  # ...and closes back below it (small body, long upper tail)
    low[-1] = 10.0  # lift the low so the lower wick stays small (tail must dominate it)
    out = INDICATORS.create("kangaroo_tail").compute(
        frame(close, high=high, low=low, open_=open_)
    )["kangaroo_tail"].to_numpy()
    np.testing.assert_array_equal(out[:20], 0.0)  # warm-up
    assert out[20] == -100.0
