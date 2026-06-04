"""Upthrust — golden + edge cases (deterministic; no reference library).

Wyckoff Upthrust (-100) is a false breakout of the prior-``N`` rolling-high resistance that the
close fails to hold (it falls back below). It is a bearish-only signal — there is no +100 case.
The first ``N`` bars are 0 (warm-up). These tests hand-build OHLC bars so the resistance level
is known exactly, then assert the documented closed-form rule.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.upthrust import upthrust  # noqa: F401  (import fires @register)

_N = 5  # short window for compact golden frames


def _upthrust(o, h, low, c, length=_N):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("upthrust", length=length).compute(df)["upthrust"].to_numpy()


# A flat plateau of ``_N`` bars at H=11/L=9/C=10 makes resistance = 11 for the bar that
# immediately follows it, so the test bar's behaviour is fully determined.
_PH = [11.0] * _N
_PL = [9.0] * _N
_PC = [10.0] * _N
_PO = [10.0] * _N


def test_upthrust_golden_hit():
    # Test bar spikes to high 11.5 (> resistance 11) but closes 10.2 (< resistance 11) -> -100.
    o = _PO + [10.5]
    h = _PH + [11.5]
    low = _PL + [10.1]
    c = _PC + [10.2]
    assert _upthrust(o, h, low, c)[_N] == -100.0


def test_upthrust_pierces_but_holds_above_is_zero():
    # High pierces resistance (11.5 > 11) but the close (11.2) is still ABOVE resistance -> a
    # genuine breakout, not an upthrust -> 0.
    o = _PO + [10.5]
    h = _PH + [11.5]
    low = _PL + [10.1]
    c = _PC + [11.2]
    assert _upthrust(o, h, low, c)[_N] == 0.0


def test_upthrust_close_exactly_on_resistance_is_zero():
    # Close lands exactly on resistance (11.0). The reject test is strict (close < resistance),
    # so an exact tie does not count -> 0.
    o = _PO + [10.5]
    h = _PH + [11.5]
    low = _PL + [10.1]
    c = _PC + [11.0]
    assert _upthrust(o, h, low, c)[_N] == 0.0


def test_upthrust_no_pierce_is_zero():
    # Stays entirely inside the range (high 10.8 <= resistance 11) -> 0 even though the close is
    # below resistance (you cannot reject a level you never reached).
    o = _PO + [10.5]
    h = _PH + [10.8]
    low = _PL + [9.5]
    c = _PC + [10.0]
    assert _upthrust(o, h, low, c)[_N] == 0.0


def test_upthrust_high_touches_resistance_is_zero():
    # High touches resistance exactly (11.0) without piercing it; the pierce test is strict
    # (high > resistance) -> 0.
    o = _PO + [10.5]
    h = _PH + [11.0]
    low = _PL + [9.5]
    c = _PC + [10.0]
    assert _upthrust(o, h, low, c)[_N] == 0.0


def test_upthrust_never_emits_plus_100():
    # Bearish-only: a strong false breakdown that would be a Spring (+100) must read 0 here, since
    # this indicator only isolates the bearish upthrust leg.
    o = _PO + [9.5]
    h = _PH + [9.9]
    low = _PL + [8.5]  # dips below the prior-low support
    c = _PC + [9.8]  # ...and reclaims it -> a Spring, not an Upthrust
    out = _upthrust(o, h, low, c)
    assert out[_N] == 0.0
    assert not np.any(out == 100.0)


def test_upthrust_constant_frame_is_zero():
    # A flat series (open == high == low == close) has resistance == price; the strict pierce
    # comparison never fires -> all 0.
    c = [10.0] * 30
    out = _upthrust(c, c, c, c)
    np.testing.assert_array_equal(out, 0.0)


def test_upthrust_warmup_is_zero():
    # The first ``length`` bars have no full prior window -> forced to 0.
    o = _PO + [10.5]
    h = _PH + [11.5]
    low = _PL + [10.1]
    c = _PC + [10.2]
    np.testing.assert_array_equal(_upthrust(o, h, low, c)[:_N], 0.0)


def test_upthrust_short_frame_is_zero():
    # Fewer bars than the window -> every output is 0.
    o = [10.0, 10.5, 10.5]
    h = [11.0, 11.5, 11.5]
    low = [9.0, 10.1, 10.1]
    c = [10.0, 10.2, 10.2]
    np.testing.assert_array_equal(_upthrust(o, h, low, c), 0.0)


def test_upthrust_output_contract():
    o = _PO + [10.5]
    h = _PH + [11.5]
    low = _PL + [10.1]
    c = _PC + [10.2]
    out = INDICATORS.create("upthrust", length=_N).compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["upthrust"]
    assert str(out["upthrust"].dtype) == "float64"
    assert set(np.unique(out["upthrust"].to_numpy())) <= {-100.0, 0.0}


def test_upthrust_default_length_is_20():
    # Default window is 20: a 21-bar frame has exactly one post-warm-up bar (index 20).
    n = 21
    high = [11.0] * n
    low = [9.0] * n
    close = [10.0] * n
    open_ = [10.0] * n
    high[-1] = 12.0  # final bar pierces resistance 11
    close[-1] = 10.5  # ...and falls back below it
    out = INDICATORS.create("upthrust").compute(
        frame(close, high=high, low=low, open_=open_)
    )["upthrust"].to_numpy()
    np.testing.assert_array_equal(out[:20], 0.0)  # warm-up
    assert out[20] == -100.0


def test_upthrust_rejects_unknown_param():
    # Params model forbids extras: a stray kwarg must raise rather than silently no-op.
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        INDICATORS.create("upthrust", window=5)
