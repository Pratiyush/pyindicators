"""VPA Effort vs Result parity — GOLDEN-ONLY (no reference library implements VSA).

There is no TA-Lib / pandas-ta / finta / ta oracle for Volume-Spread-Analysis, so instead of
comparing against a library we pin the *closed-form definition* with a fully independent
re-implementation (plain pandas, a different code path from the indicator) and require an exact
match on both the deterministic synthetic frame AND real market data. This is the structural
parity check called for when an indicator is golden-only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS


def _reference(df: pd.DataFrame, length: int, effort_mult: float, result_mult: float) -> np.ndarray:
    """Independent reference implementation of the documented VSA rule."""
    spread = df["high"] - df["low"]
    effort = df["volume"] / df["volume"].rolling(length).mean()
    result = spread / spread.rolling(length).mean()
    rng = spread.to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        mfm = ((df["close"] - df["low"]) - (df["high"] - df["close"])).to_numpy() / rng
    mfm = np.where(rng == 0.0, 0.0, mfm)  # zero-spread -> 0 (matches safe_divide fill)
    anomaly = (effort.to_numpy() >= effort_mult) & (result.to_numpy() <= result_mult)
    return np.where(anomaly & (mfm > 0.0), 1.0, np.where(anomaly & (mfm < 0.0), -1.0, 0.0))


def _check(df, *, length=20, effort_mult=2.0, result_mult=0.7):
    out = INDICATORS.create(
        "vpa_effort_vs_result",
        length=length,
        effort_mult=effort_mult,
        result_mult=result_mult,
    ).compute(df)["vpa_effort_vs_result"]
    ref = _reference(df, length, effort_mult, result_mult)
    # Exact: the output is a categorical -1/0/+1 decision, so no tolerance is warranted.
    np.testing.assert_array_equal(out.to_numpy(), ref)


def test_definition_parity_synthetic():
    _check(deterministic_frame())


def test_definition_parity_real_data():
    _check(real_frame())  # genuine AAPL daily bars — real gaps, real volume spikes


def test_definition_parity_alt_params():
    # A second parameter point so the rule isn't pinned to a single threshold set.
    df = deterministic_frame()
    _check(df, length=10, effort_mult=1.5, result_mult=0.9)


def test_real_data_actually_fires_both_signs():
    # Sanity: on real data the rule should produce some +1 and some -1 (loose thresholds), so the
    # parity above isn't trivially comparing all-zero arrays.
    out = INDICATORS.create(
        "vpa_effort_vs_result", length=20, effort_mult=1.3, result_mult=1.0
    ).compute(real_frame())["vpa_effort_vs_result"]
    vals = set(np.unique(out.to_numpy()).tolist())
    assert 1.0 in vals and -1.0 in vals
