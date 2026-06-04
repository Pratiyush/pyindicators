"""Connors RSI — golden / closed-form components + edge cases (no single library oracle)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.momentum.crsi import _percent_rank, _streak, crsi  # noqa: F401 (registers crsi)
from pyindicators.momentum.rsi import rsi


def test_streak_closed_form():
    # up, up, down, down, down, flat, up: signed consecutive-close run lengths.
    close = pd.Series([10.0, 11.0, 12.0, 11.0, 10.0, 9.0, 9.0, 10.0])
    expected = [0.0, 1.0, 2.0, -1.0, -2.0, -3.0, 0.0, 1.0]
    np.testing.assert_array_equal(_streak(close).to_numpy(), expected)


def test_percent_rank_nan_current_is_nan():
    # a NaN current value at i >= length yields NaN (covers the cur-NaN skip path)
    s = pd.Series([float(i) for i in range(8)] + [np.nan] + [float(i) for i in range(9, 16)])
    out = _percent_rank(s, 5)
    assert np.isnan(out.iloc[8])


def test_percent_rank_closed_form():
    # With length=3 the value at index 3 ranks against the prior 3 values [1,2,3]: two (<3) -> 66.67%.
    s = pd.Series([1.0, 2.0, 3.0, 2.5, 5.0])
    pr = _percent_rank(s, 3)
    assert np.isnan(pr.iloc[:3]).all()  # first ``length`` entries are warm-up
    np.testing.assert_allclose(pr.iloc[3], 100.0 * 2 / 3)  # [1,2,3] < 2.5 -> 2
    np.testing.assert_allclose(pr.iloc[4], 100.0 * 3 / 3)  # [2,3,2.5] < 5 -> 3 -> 100


def test_percent_rank_bounds_and_ties():
    # All-equal prior window -> nothing strictly less than current -> 0%.
    s = pd.Series([5.0, 5.0, 5.0, 5.0, 5.0])
    assert _percent_rank(s, 3).iloc[3] == 0.0


def test_crsi_is_mean_of_three_components():
    # The composite must equal the explicit average of its three published parts.
    df = deterministic_frame(300)
    close = df["close"]
    out = INDICATORS.create("crsi", rsi_length=3, streak_length=2, rank_length=100).compute(df)["crsi"]
    from pyindicators.momentum.crsi import _percent_rank as pr
    from pyindicators.momentum.roc import roc

    part1 = rsi(close, 3)
    part2 = rsi(_streak(close), 2)
    part3 = pr(roc(close, length=1), 100)
    expected = (part1 + part2 + part3) / 3.0
    np.testing.assert_allclose(out.to_numpy(), expected.to_numpy(), rtol=1e-12, equal_nan=True)


def test_crsi_within_bounds_on_real_walk():
    out = INDICATORS.create("crsi").compute(deterministic_frame(400))["crsi"]
    v = out.dropna().to_numpy()
    assert v.size > 50
    assert (v >= 0.0).all() and (v <= 100.0).all()
    assert v.std() > 0  # genuinely varies, not pinned to a constant


def test_crsi_constant_series_is_nan():
    # A flat series: every component degenerates (RSI 0/0 -> NaN), so the composite is NaN.
    out = INDICATORS.create("crsi").compute(frame([100.0] * 200))["crsi"]
    assert out.isna().all()


def test_crsi_short_frame_all_nan():
    # Fewer bars than the percent-rank warm-up -> no finite output at all.
    out = INDICATORS.create("crsi", rank_length=100).compute(frame(np.arange(1.0, 30.0)))["crsi"]
    assert out.isna().all()


def test_crsi_warmup_first_valid_index():
    # roc(1) is first valid at index 1; the prior-100 percent-rank window fills at index 101.
    out = INDICATORS.create("crsi", rsi_length=3, streak_length=2, rank_length=100).compute(
        deterministic_frame(300)
    )["crsi"]
    assert out.iloc[:101].isna().all()
    assert np.isfinite(out.iloc[101])


def test_crsi_pure_uptrend_price_rsi_saturates():
    # Strictly rising closes -> no losses -> RSI(close,3) == 100 and streak RSI == 100, so the
    # composite is (100 + 100 + PercentRank)/3 with PercentRank in [0, 100]; hence CRSI lies in
    # [66.67, 100] and 3*CRSI-200 recovers the (bounded) percent-rank leg exactly.
    close = np.linspace(100.0, 400.0, 250)  # strictly increasing closes
    df = frame(close)
    out = INDICATORS.create("crsi", rsi_length=3, streak_length=2, rank_length=100).compute(df)["crsi"]
    tail = out.dropna().to_numpy()
    assert tail.size > 50
    assert (tail >= 200.0 / 3.0 - 1e-9).all() and (tail <= 100.0 + 1e-9).all()
    pr_leg = 3.0 * tail - 200.0  # the isolated percent-rank component
    assert (pr_leg >= -1e-9).all() and (pr_leg <= 100.0 + 1e-9).all()
    # Cross-check the two saturated RSI legs explicitly on the strictly-rising series.
    np.testing.assert_allclose(rsi(df["close"], 3).dropna().to_numpy(), 100.0, atol=1e-9)
    np.testing.assert_allclose(rsi(_streak(df["close"]), 2).dropna().to_numpy(), 100.0, atol=1e-9)


def test_crsi_output_contract():
    df = deterministic_frame(200)
    out = INDICATORS.create("crsi").compute(df)
    assert list(out.columns) == ["crsi"]
    assert out["crsi"].dtype == np.float64
    assert len(out) == len(df)
