"""Spring — golden + edge cases (deterministic; no reference library).

Wyckoff Spring (+100) is a false breakdown of the prior-``N`` rolling-low support that the
close reclaims; Upthrust (-100) is the bearish mirror against the prior-``N`` rolling-high
resistance. The first ``N`` bars are 0 (warm-up). These tests hand-build OHLC bars so the
support/resistance levels are known exactly, then assert the documented rule.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.spring import spring  # noqa: F401  (import fires @register)

_N = 5  # short window for compact golden frames


def _spring(o, h, low, c, length=_N):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("spring", length=length).compute(df)["spring"].to_numpy()


# A flat plateau of ``_N`` bars at H=11/L=9/C=10 makes support = 9 and resistance = 11 for the
# bar that immediately follows it, so the test bar's behaviour is fully determined.
_PH = [11.0] * _N
_PL = [9.0] * _N
_PC = [10.0] * _N
_PO = [10.0] * _N


def test_spring_golden_hit():
    # Test bar dips to low 8.5 (< support 9) but closes 9.8 (> support 9) -> bullish spring +100.
    o = _PO + [9.5]
    h = _PH + [9.9]
    low = _PL + [8.5]
    c = _PC + [9.8]
    assert _spring(o, h, low, c)[_N] == 100.0


def test_upthrust_golden_hit():
    # Test bar spikes to high 11.5 (> resistance 11) but closes 10.2 (< resistance 11) -> -100.
    o = _PO + [10.5]
    h = _PH + [11.5]
    low = _PL + [10.1]
    c = _PC + [10.2]
    assert _spring(o, h, low, c)[_N] == -100.0


def test_spring_pierces_but_does_not_reclaim_is_zero():
    # Low dips below support (8.5 < 9) but the close (8.7) is still BELOW support -> a genuine
    # breakdown, not a spring -> 0.
    o = _PO + [9.5]
    h = _PH + [9.0]
    low = _PL + [8.5]
    c = _PC + [8.7]
    assert _spring(o, h, low, c)[_N] == 0.0


def test_spring_close_exactly_on_support_is_zero():
    # Close lands exactly on support (9.0). The reclaim test is strict (close > support), so an
    # exact tie does not count -> 0.
    o = _PO + [9.5]
    h = _PH + [9.5]
    low = _PL + [8.5]
    c = _PC + [9.0]
    assert _spring(o, h, low, c)[_N] == 0.0


def test_spring_no_pierce_is_zero():
    # Stays entirely inside the range (low 9.2 >= support 9, high 10.8 <= resistance 11) -> 0.
    o = _PO + [9.5]
    h = _PH + [10.8]
    low = _PL + [9.2]
    c = _PC + [10.0]
    assert _spring(o, h, low, c)[_N] == 0.0


def test_spring_low_touches_support_is_zero():
    # Low touches support exactly (9.0) without piercing it; the pierce test is strict
    # (low < support) -> 0.
    o = _PO + [9.5]
    h = _PH + [10.0]
    low = _PL + [9.0]
    c = _PC + [9.8]
    assert _spring(o, h, low, c)[_N] == 0.0


def test_spring_constant_frame_is_zero():
    # A flat series (open == high == low == close) has support == resistance == price; strict
    # comparisons never fire -> all 0.
    c = [10.0] * 30
    out = _spring(c, c, c, c)
    np.testing.assert_array_equal(out, 0.0)


def test_spring_warmup_is_zero():
    # The first ``length`` bars have no full prior window -> forced to 0.
    o = _PO + [9.5]
    h = _PH + [9.9]
    low = _PL + [8.5]
    c = _PC + [9.8]
    np.testing.assert_array_equal(_spring(o, h, low, c)[:_N], 0.0)


def test_spring_short_frame_is_zero():
    # Fewer bars than the window -> every output is 0.
    o = [10.0, 9.5, 9.5]
    h = [11.0, 9.9, 9.9]
    low = [9.0, 8.5, 8.5]
    c = [10.0, 9.8, 9.8]
    np.testing.assert_array_equal(_spring(o, h, low, c), 0.0)


def test_spring_output_contract():
    o = _PO + [9.5]
    h = _PH + [9.9]
    low = _PL + [8.5]
    c = _PC + [9.8]
    out = INDICATORS.create("spring", length=_N).compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["spring"]
    assert str(out["spring"].dtype) == "float64"
    assert set(np.unique(out["spring"].to_numpy())) <= {-100.0, 0.0, 100.0}


def test_spring_default_length_is_20():
    # Default window is 20: a 21-bar frame has exactly one post-warm-up bar (index 20).
    n = 21
    high = [11.0] * n
    low = [9.0] * n
    close = [10.0] * n
    open_ = [10.0] * n
    low[-1] = 8.0  # final bar pierces support 9
    close[-1] = 9.5  # ...and reclaims it
    out = INDICATORS.create("spring").compute(
        frame(close, high=high, low=low, open_=open_)
    )["spring"].to_numpy()
    np.testing.assert_array_equal(out[:20], 0.0)  # warm-up
    assert out[20] == 100.0
