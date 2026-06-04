"""Piercing — golden + edge cases (deterministic; no reference library).

All golden values were cross-checked against ``talib.CDLPIERCING`` (see the parity test for
the exact, no-tolerance comparison on synthetic + real bars).
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.piercing import piercing  # noqa: F401  (import fires @register)

# 11 warm-up bars (body 2.0) so the BodyLong average is 2.0 by the time the pattern forms at
# bar 11 (long black) -> bar 12 (long white pierce).
_WARM = 11
_WO = [100.0] * _WARM
_WC = [102.0] * _WARM
_WH = [102.5] * _WARM
_WL = [99.5] * _WARM


def _pierce(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("piercing").compute(df)["piercing"].to_numpy()


def _build(open12, close12, *, high12=None, low12=None):
    # bar 11: long BLACK (110 -> 100, body 10, low 99.5).
    # bar 12: long WHITE pierce, parameterised by its open/close.
    o = _WO + [110.0, open12]
    c = _WC + [100.0, close12]
    h = _WH + [110.5, close12 + 0.5 if high12 is None else high12]
    low = _WL + [99.5, open12 - 0.5 if low12 is None else low12]
    return o, h, low, c


def test_piercing_bullish_valid():
    # White opens below prior low (99 < 99.5) and closes at 106, above the prior midpoint
    # (close[prev] + body*0.5 = 100 + 5 = 105) but within the prior body (< 110) -> +100.
    assert _pierce(*_build(99.0, 106.0))[12] == 100.0


def test_piercing_insufficient_pierce_is_zero():
    # Close 104 < midpoint 105 -> the white body does not pierce far enough -> 0.
    assert _pierce(*_build(99.0, 104.0))[12] == 0.0


def test_piercing_no_gap_below_is_zero():
    # Open 100 is not below the prior low 99.5 (no downward gap) -> 0.
    assert _pierce(*_build(100.0, 106.0))[12] == 0.0


def test_piercing_close_above_prior_body_is_zero():
    # Close 111 > prior open 110: closes above (not within) the prior body -> 0 (engulf, not
    # a pierce).
    assert _pierce(*_build(99.0, 111.0, high12=111.5))[12] == 0.0


def test_piercing_warmup_is_zero():
    np.testing.assert_array_equal(_pierce(*_build(99.0, 106.0))[:11], 0.0)  # lookback = 11


def test_piercing_constant_frame_is_zero():
    n = 30
    o = h = low = c = [100.0] * n
    out = _pierce(o, h, low, c)
    np.testing.assert_array_equal(out, np.zeros(n))


def test_piercing_short_frame_is_zero():
    # Fewer bars than the 11-bar lookback -> all zeros (no pattern can form).
    o = h = low = c = [100.0, 101.0, 100.0, 99.0, 100.0]
    out = _pierce(o, h, low, c)
    np.testing.assert_array_equal(out, np.zeros(5))


def test_piercing_output_contract():
    o, h, low, c = _build(99.0, 106.0)
    out = INDICATORS.create("piercing").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["piercing"]
    # Piercing is bullish-only: 0 or +100, never negative, never the ±80 partial score.
    assert set(np.unique(out["piercing"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
