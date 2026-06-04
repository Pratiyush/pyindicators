"""Big Shadow — golden + edge cases (deterministic; no reference library, golden-only).

Big Shadow has no oracle in any reference lib, so correctness is pinned here by constructed
bars with known outcomes: a calm run of equal-range bars (so the trailing average range is a
known constant) followed by one wide bar that either does or does not engulf / exceed the
threshold. ``avg_period`` is kept small so a short, readable frame still clears warm-up.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.big_shadow import big_shadow  # noqa: F401  (import fires @register)

# Three calm bars of range 1.0 each give a trailing avg_range of 1.0 at bar 3 (period=3).
# Bar 3 is the candidate Big Shadow. With factor=2.0 it must have range > 2.0 to be "wide".
_CALM_O = [10.0, 10.0, 10.0]
_CALM_H = [10.5, 10.5, 10.5]
_CALM_L = [9.5, 9.5, 9.5]
_CALM_C = [10.0, 10.0, 10.0]  # range = high - low = 1.0 for each calm bar


def _bs(o, h, low, c, *, avg_period=3, factor=2.0):
    df = frame(c, high=h, low=low, open_=o)
    ind = INDICATORS.create("big_shadow", avg_period=avg_period, factor=factor)
    return ind.compute(df)["big_shadow"].to_numpy()


def test_bullish_wide_engulfing_is_plus_100():
    # Bar 3: range 3.0 (> 2*1.0), high 12 > prev high 10.5, low 9 < prev low 9.5, closes up.
    out = _bs(
        _CALM_O + [9.0], _CALM_H + [12.0], _CALM_L + [9.0], _CALM_C + [11.5]
    )
    assert out[3] == 100.0


def test_bearish_wide_engulfing_is_minus_100():
    # Same wide engulfing bar but closing down (open 11.5 -> close 9.5) -> black -> -100.
    out = _bs(
        _CALM_O + [11.5], _CALM_H + [12.0], _CALM_L + [9.0], _CALM_C + [9.5]
    )
    assert out[3] == -100.0


def test_wide_but_not_engulfing_is_zero():
    # Range 3.0 is wide, but high 12 > prev high while low 9.6 does NOT pierce prev low 9.5,
    # so it fails the range-engulf test -> 0.
    out = _bs(
        _CALM_O + [9.6], _CALM_H + [12.6], _CALM_L + [9.6], _CALM_C + [11.5]
    )
    assert out[3] == 0.0


def test_engulfing_but_not_wide_is_zero():
    # Engulfs (high 11 > 10.5, low 9 < 9.5) but range 2.0 is NOT > factor*avg (2.0*1.0) -> 0.
    out = _bs(
        _CALM_O + [9.5], _CALM_H + [11.0], _CALM_L + [9.0], _CALM_C + [10.5]
    )
    assert out[3] == 0.0


def test_strict_threshold_excludes_exact_factor_multiple():
    # range exactly == factor*avg (2.0) is NOT wide (strict >), even while engulfing -> 0.
    out = _bs(
        _CALM_O + [9.4], _CALM_H + [11.0], _CALM_L + [9.0], _CALM_C + [10.6], factor=2.0
    )
    # high 11 > 10.5, low 9.0 < 9.5 (engulfs); range = 2.0 == 2.0*avg -> not strictly wide.
    assert out[3] == 0.0


def test_warmup_bars_are_zero():
    # The first avg_period bars cannot have a full trailing window -> always 0, even if a
    # bar is itself wide/engulfing relative to nothing.
    out = _bs(
        _CALM_O + [9.0], _CALM_H + [12.0], _CALM_L + [9.0], _CALM_C + [11.5], avg_period=3
    )
    np.testing.assert_array_equal(out[:3], 0.0)


def test_doji_wide_engulfing_counts_as_white():
    # close == open (doji) is treated as white (color +1, matching candle_color) -> +100.
    out = _bs(
        _CALM_O + [10.0], _CALM_H + [12.0], _CALM_L + [9.0], _CALM_C + [10.0]
    )
    assert out[3] == 100.0


def test_higher_factor_makes_signal_rarer():
    # The same wide engulfing bar (range 3.0) fires at factor 2.0 but not at factor 4.0.
    args = (_CALM_O + [9.0], _CALM_H + [12.0], _CALM_L + [9.0], _CALM_C + [11.5])
    assert _bs(*args, factor=2.0)[3] == 100.0
    assert _bs(*args, factor=4.0)[3] == 0.0
