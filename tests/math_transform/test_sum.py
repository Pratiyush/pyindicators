"""Rolling SUM — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.sum import sum  # noqa: A004,F401 - import fires @register


def test_sum_closed_form_small_window():
    # Window of 3 over a hand-checked series: each value is the total of itself and the two
    # preceding closes; the first two bars are NaN (undersized window).
    out = INDICATORS.create("sum", length=3).compute(frame([5.0, 3.0, 4.0, 2.0, 6.0, 1.0]))["sum"]
    assert out.iloc[:2].isna().all()
    np.testing.assert_array_equal(out.iloc[2:].to_numpy(), [12.0, 9.0, 12.0, 9.0])


def test_sum_constant_series_is_length_times_level():
    # A flat window sums to length * the constant level once the window fills.
    out = INDICATORS.create("sum", length=4).compute(frame([7.0] * 10))["sum"]
    assert out.iloc[:3].isna().all()
    np.testing.assert_array_equal(out.iloc[3:].to_numpy(), np.full(7, 28.0))


def test_sum_relates_to_sma_by_length():
    # SUM is the unscaled SMA: SUM / length == SMA over the same window.
    df = deterministic_frame(120)
    s = INDICATORS.create("sum", length=10).compute(df)["sum"]
    m = INDICATORS.create("sma", length=10).compute(df)["sma"]
    mask = s.notna() & m.notna()
    assert mask.sum() > 80
    np.testing.assert_allclose((s[mask] / 10.0).to_numpy(), m[mask].to_numpy(), rtol=1e-12)


def test_sum_arithmetic_progression_closed_form():
    # On 1..20 with window 5, each finite sum is 5 consecutive integers ending at the bar:
    # sum_{k=i-4}^{i} k = 5*i - 10.
    closes = np.arange(1.0, 21.0)
    out = INDICATORS.create("sum", length=5).compute(frame(closes))["sum"]
    np.testing.assert_array_equal(out.iloc[4:].to_numpy(), 5.0 * closes[4:] - 10.0)


def test_sum_length_one_is_passthrough():
    closes = [3.0, 1.0, 4.0, 1.0, 5.0]
    out = INDICATORS.create("sum", length=1).compute(frame(closes))["sum"]
    np.testing.assert_array_equal(out.to_numpy(), closes)


def test_sum_short_frame_all_nan():
    out = INDICATORS.create("sum", length=30).compute(frame([1.0, 2.0, 3.0]))["sum"]
    assert out.isna().all()


def test_sum_warmup_and_contract():
    df = deterministic_frame(200)
    out = INDICATORS.create("sum", length=30).compute(df)
    assert list(out.columns) == ["sum"]
    assert out["sum"].dtype == np.float64
    assert len(out) == len(df)
    assert out["sum"].iloc[:29].isna().all()
    assert out["sum"].iloc[29:].notna().all()
