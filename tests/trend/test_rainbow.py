"""Rainbow Charts — golden (closed-form) + edge cases.

Import the module directly so ``@INDICATORS.register`` fires under isolated test selection.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.rainbow import NUM_RIBBONS  # noqa: F401  (ensures registration)

RIBBONS = [f"rainbow_{i}" for i in range(1, NUM_RIBBONS + 1)]


def test_rainbow_linear_ramp_closed_form():
    # On a unit-slope line, each SMA(length=2) pass shifts the line back by exactly 0.5, so
    # ribbon_k(i) = i - 0.5*k for i >= k, and NaN during the k-bar warm-up. This pins every
    # ribbon to an exact analytic value (no reference lib needed).
    n = 40
    out = INDICATORS.create("rainbow", length=2).compute(frame(np.arange(float(n))))
    idx = np.arange(float(n))
    for k in range(1, NUM_RIBBONS + 1):
        expected = idx - 0.5 * k
        expected[:k] = np.nan
        np.testing.assert_allclose(out[f"rainbow_{k}"].to_numpy(), expected, equal_nan=True)


def test_rainbow_constant_series_collapses_to_constant():
    # No price variation -> every ribbon equals the constant once it clears warm-up.
    out = INDICATORS.create("rainbow", length=3).compute(frame(np.full(30, 7.0)))
    for col in RIBBONS:
        np.testing.assert_allclose(out[col].dropna().to_numpy(), 7.0)


def test_rainbow_outputs_and_monotone_warmup():
    # Exactly NUM_RIBBONS columns, and warm-up grows by (length-1) per deeper ribbon:
    # ribbon_k is NaN for the first k*(length-1) bars (here length=3 -> 2 per ribbon).
    length = 3
    out = INDICATORS.create("rainbow", length=length).compute(deterministic_frame(200))
    assert list(out.columns) == RIBBONS
    for k in range(1, NUM_RIBBONS + 1):
        assert int(out[f"rainbow_{k}"].isna().sum()) == k * (length - 1)


def test_rainbow_default_length_is_two():
    # Default length=2 -> each deeper ribbon costs exactly one more warm-up bar.
    out = INDICATORS.create("rainbow").compute(deterministic_frame(120))
    for k in range(1, NUM_RIBBONS + 1):
        assert int(out[f"rainbow_{k}"].isna().sum()) == k


def test_rainbow_causal_prefix_independent_of_future():
    # Truncating the future must not change any already-emitted ribbon value (no look-ahead).
    df = deterministic_frame(150)
    full = INDICATORS.create("rainbow", length=2).compute(df)
    cut = 90
    head = INDICATORS.create("rainbow", length=2).compute(df.iloc[:cut])
    for col in RIBBONS:
        np.testing.assert_allclose(
            full[col].to_numpy()[:cut], head[col].to_numpy(), equal_nan=True
        )


def test_rainbow_short_frame_all_nan():
    # Too few bars to seed even the first SMA -> the whole fan is NaN (no fabricated values).
    out = INDICATORS.create("rainbow", length=4).compute(frame([1.0, 2.0, 3.0]))
    assert out.isna().all().all()
