"""Percent Rank — golden values, closed-form structure, and edge cases.

Import the module directly so ``@INDICATORS.register`` fires for the parallel-build layout
(utils is not yet wired into the top-level package by a coordinator). Closed-form assertions
live here: an explicit small-window rank, the strictly-rising -> 100 / falling -> 0 / flat -> 0
extremes, tie exclusion (``<`` not ``<=``), the ``length``-bar warm-up, and the [0,100] range.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.utils import percent_rank as pr_mod  # noqa: F401  (triggers registration)


def _brute(close: np.ndarray, length: int) -> np.ndarray:
    """Independent per-window oracle: percent of the prior ``length`` values strictly below
    the current close. Plain Python loop, no stride tricks — the reference definition."""
    n = close.size
    out = np.full(n, np.nan)
    for i in range(length, n):
        window = close[i - length : i]
        out[i] = 100.0 * int(np.sum(window < close[i])) / length
    return out


def test_percent_rank_golden_small_window():
    # length=3. For bar i the prior window is close[i-3:i]:
    #   i=3 close=4.0  prior=[1,2,3]   all below   -> 3/3 = 100
    #   i=4 close=2.5  prior=[2,3,4]   {2} below   -> 1/3 = 33.333...
    #   i=5 close=0.0  prior=[3,4,2.5] none below  -> 0
    close = [1.0, 2.0, 3.0, 4.0, 2.5, 0.0]
    out = INDICATORS.create("percent_rank", length=3).compute(frame(close))["percent_rank"]
    assert out.iloc[:3].isna().all()  # warm-up: first `length` bars
    np.testing.assert_allclose(
        out.to_numpy()[3:], [100.0, 100.0 / 3.0, 0.0], rtol=1e-12, atol=1e-12
    )


def test_percent_rank_matches_brute_force_oracle():
    # Vectorised implementation == explicit per-window loop, bar for bar, on a real walk.
    length = 100
    df = deterministic_frame(400)
    out = INDICATORS.create("percent_rank", length=length).compute(df)["percent_rank"].to_numpy()
    expected = _brute(df["close"].to_numpy(dtype="float64"), length)
    np.testing.assert_allclose(out, expected, rtol=1e-12, atol=1e-12, equal_nan=True)


def test_percent_rank_strictly_rising_is_100():
    # Every prior value is below the current -> a fresh high every bar -> 100.
    out = INDICATORS.create("percent_rank", length=5).compute(frame(np.arange(1.0, 40.0)))[
        "percent_rank"
    ]
    np.testing.assert_allclose(out.dropna().to_numpy(), 100.0, atol=1e-12)


def test_percent_rank_strictly_falling_is_0():
    # No prior value is below the current -> 0.
    out = INDICATORS.create("percent_rank", length=5).compute(frame(np.arange(40.0, 1.0, -1.0)))[
        "percent_rank"
    ]
    np.testing.assert_allclose(out.dropna().to_numpy(), 0.0, atol=1e-12)


def test_percent_rank_flat_window_is_0_not_nan():
    # A constant series has nothing *strictly* below -> 0. There is no division to guard, so
    # (unlike rank-with-<=) the result is a finite 0, never NaN.
    out = INDICATORS.create("percent_rank", length=4).compute(frame(np.full(20, 7.5)))[
        "percent_rank"
    ]
    tail = out.dropna()
    assert len(tail) == 16
    np.testing.assert_allclose(tail.to_numpy(), 0.0, atol=1e-12)


def test_percent_rank_ties_are_excluded():
    # Strictly-below means equal prior values are NOT counted. prior=[2,5,5], current=5 -> 1/3.
    out = INDICATORS.create("percent_rank", length=3).compute(frame([0.0, 2.0, 5.0, 5.0, 5.0]))[
        "percent_rank"
    ]
    assert out.iloc[-1] == pytest.approx(100.0 / 3.0, rel=1e-12)


def test_percent_rank_warmup_is_exactly_length_bars():
    # The first `length` bars lack a full prior window -> NaN; bar `length` is the first value.
    length = 10
    out = INDICATORS.create("percent_rank", length=length).compute(
        frame(deterministic_frame(50)["close"].to_numpy())
    )["percent_rank"]
    assert out.iloc[:length].isna().all()
    assert out.iloc[length:].notna().all()


def test_percent_rank_within_bounds():
    out = INDICATORS.create("percent_rank", length=100).compute(deterministic_frame(400))[
        "percent_rank"
    ]
    finite = out.dropna().to_numpy()
    assert finite.size > 0
    assert (finite >= 0.0).all() and (finite <= 100.0).all()


def test_percent_rank_length_one_is_sign_of_one_bar_change():
    # length=1: window is the single prior close. close[i] > close[i-1] -> 100, else 0.
    close = [10.0, 11.0, 11.0, 9.0, 12.0]
    out = INDICATORS.create("percent_rank", length=1).compute(frame(close))["percent_rank"]
    assert np.isnan(out.iloc[0])
    np.testing.assert_allclose(out.to_numpy()[1:], [100.0, 0.0, 0.0, 100.0], atol=1e-12)


def test_percent_rank_short_frame_all_nan():
    # Fewer than length+1 rows -> no full prior window anywhere -> all NaN.
    out = INDICATORS.create("percent_rank", length=100).compute(frame([1.0, 2.0, 3.0]))[
        "percent_rank"
    ]
    assert out.isna().all()


def test_percent_rank_exactly_length_rows_all_nan():
    # With exactly `length` rows the current bar can never see a full prior window -> all NaN.
    length = 5
    out = INDICATORS.create("percent_rank", length=length).compute(frame(np.arange(1.0, 6.0)))[
        "percent_rank"
    ]
    assert out.isna().all()


def test_percent_rank_is_causal_truncation_invariant():
    # Each bar reads only its prior window, so truncating the tail leaves earlier bars unchanged.
    df = deterministic_frame(200)
    full = INDICATORS.create("percent_rank", length=50).compute(df)["percent_rank"]
    trunc = INDICATORS.create("percent_rank", length=50).compute(df.iloc[:120].copy())[
        "percent_rank"
    ]
    pd.testing.assert_series_equal(full.iloc[:120], trunc, check_exact=False, rtol=1e-12)


def test_percent_rank_single_row_all_nan():
    out = INDICATORS.create("percent_rank", length=100).compute(frame([42.0]))["percent_rank"]
    assert out.isna().all()


def test_percent_rank_rejects_unknown_param():
    with pytest.raises((TypeError, ValueError)):
        INDICATORS.create("percent_rank", window=10)
