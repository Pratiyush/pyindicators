"""Beta — golden (closed-form regression slope) + edge cases.

Imports the module directly so ``@INDICATORS.register`` fires under standalone runs, then
drives everything through ``INDICATORS.create`` like the rest of the suite.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.statistics.beta import beta  # noqa: F401  (registers the indicator)


def _frame_from_returns(high_ret, low_ret, *, h0=100.0, l0=80.0):
    """Build an OHLCV frame whose high/low have exactly the given one-period returns."""
    high = h0 * np.cumprod(1.0 + np.r_[0.0, np.asarray(high_ret, dtype="float64")])
    low = l0 * np.cumprod(1.0 + np.r_[0.0, np.asarray(low_ret, dtype="float64")])
    return frame(high, high=high, low=low)


def test_beta_recovers_exact_slope():
    # If low-returns == b * high-returns exactly, the regression slope is b on every window.
    rng = np.random.default_rng(1)
    high_ret = rng.normal(0.0, 0.01, 30)
    out = INDICATORS.create("beta", length=5).compute(
        _frame_from_returns(high_ret, 2.0 * high_ret)
    )["beta"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 2.0, atol=1e-10)


def test_beta_intercept_does_not_change_slope():
    # An affine relation low_ret = 0.5*high_ret + c has slope 0.5 regardless of the offset c.
    rng = np.random.default_rng(2)
    high_ret = rng.normal(0.0, 0.01, 30)
    out = INDICATORS.create("beta", length=5).compute(
        _frame_from_returns(high_ret, 0.5 * high_ret + 0.003)
    )["beta"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 0.5, atol=1e-10)


def test_beta_flat_high_is_zero_after_warmup():
    # Flat high -> zero return variance -> denominator 0 -> TA-Lib emits 0.0 (warm-up stays NaN).
    f = frame(np.full(12, 50.0), high=np.full(12, 50.0), low=np.linspace(40.0, 45.0, 12))
    out = INDICATORS.create("beta", length=5).compute(f)["beta"].to_numpy()
    assert np.isnan(out[:5]).all()
    np.testing.assert_array_equal(out[5:], 0.0)


def test_beta_warmup_is_length_nans():
    # First valid value needs ``length`` return-pairs, i.e. index ``length`` (pct_change drops 0).
    high_ret = np.random.default_rng(3).normal(0, 0.01, 20)
    low_ret = np.random.default_rng(33).normal(0, 0.01, 20)
    out = INDICATORS.create("beta", length=5).compute(
        _frame_from_returns(high_ret, low_ret)
    )["beta"]
    assert out.iloc[:5].isna().all()
    assert out.iloc[5:].notna().all()


def test_beta_short_frame_all_nan():
    out = INDICATORS.create("beta", length=5).compute(
        frame([1.0, 2.0, 3.0], high=[1.0, 2.0, 3.0], low=[0.5, 1.0, 1.5])
    )["beta"]
    assert out.isna().all()


def test_beta_output_contract():
    rng = np.random.default_rng(4)
    f = _frame_from_returns(rng.normal(0, 0.01, 40), rng.normal(0, 0.01, 40))
    res = INDICATORS.create("beta", length=5).compute(f)
    assert list(res.columns) == ["beta"]
    assert len(res) == len(f)
    assert res["beta"].dtype == np.float64


def test_beta_function_matches_registry():
    rng = np.random.default_rng(5)
    f = _frame_from_returns(rng.normal(0, 0.01, 30), rng.normal(0, 0.01, 30))
    direct = beta(f["high"], f["low"], 5)
    viareg = INDICATORS.create("beta", length=5).compute(f)["beta"]
    pd.testing.assert_series_equal(direct.rename("beta"), viareg, check_names=True)
