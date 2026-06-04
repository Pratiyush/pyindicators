"""ROC1 — golden + edge cases.

Importing the module directly registers ROC1 (utils is not wired into the top-level package
yet). Closed-form assertions live here: explicit formula, equivalence to ``roc`` at length 1,
the first-bar NaN, and the zero-prior-close guard.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.momentum.roc import roc
from pyindicators.utils import roc1  # noqa: F401  (import fires @INDICATORS.register)


def test_roc1_matches_explicit_formula():
    close = np.array([10.0, 11.0, 9.9, 9.9, 12.0])
    out = INDICATORS.create("roc1").compute(frame(close))["roc1"]
    expected = 100.0 * (close[1:] / close[:-1] - 1.0)
    assert np.isnan(out.iloc[0])
    np.testing.assert_allclose(out.to_numpy()[1:], expected, rtol=1e-12, atol=1e-12)


def test_roc1_equals_roc_length_1():
    df = deterministic_frame(200)
    ours = INDICATORS.create("roc1").compute(df)["roc1"]
    ref = roc(df["close"], length=1)
    np.testing.assert_allclose(ours.to_numpy(), ref.to_numpy(), rtol=1e-12, equal_nan=True)


def test_roc1_first_bar_is_nan():
    out = INDICATORS.create("roc1").compute(frame([100.0, 101.0, 102.0]))["roc1"]
    assert np.isnan(out.iloc[0])
    assert out.iloc[1:].notna().all()


def test_roc1_zero_prior_close_is_guarded_to_nan():
    # Prior close == 0 would divide by zero; the guard yields NaN, not +/-inf.
    out = INDICATORS.create("roc1").compute(frame([0.0, 5.0, 6.0]))["roc1"]
    assert np.isnan(out.iloc[1])
    assert np.isfinite(out.iloc[2])


def test_roc1_constant_series_is_zero():
    out = INDICATORS.create("roc1").compute(frame([50.0, 50.0, 50.0, 50.0]))["roc1"]
    np.testing.assert_allclose(out.to_numpy()[1:], 0.0, atol=1e-12)


def test_roc1_single_row_all_nan():
    out = INDICATORS.create("roc1").compute(frame([42.0]))["roc1"]
    assert out.isna().all()


def test_roc1_takes_no_params():
    import pytest

    with pytest.raises((TypeError, ValueError)):
        INDICATORS.create("roc1", length=5)
