"""Rolling Covariance (high vs low) — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.statistics.covariance import covariance  # noqa: F401  (fires @register)


def test_covariance_closed_form_last_window():
    # Sample covariance (ddof=1) of the last length=3 window, computed by hand.
    high = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    low = [2.0, 1.0, 4.0, 3.0, 6.0, 5.0]
    out = INDICATORS.create("covariance", length=3).compute(
        frame(high, high=high, low=low)
    )["covariance"]
    x = np.array([4.0, 5.0, 6.0])
    y = np.array([3.0, 6.0, 5.0])
    expected = np.cov(x, y, ddof=1)[0, 1]
    np.testing.assert_allclose(out.iloc[-1], expected, atol=1e-12)


def test_covariance_warmup_is_nan():
    high = [1.0, 2.0, 3.0, 4.0, 5.0]
    low = [5.0, 4.0, 3.0, 2.0, 1.0]
    out = INDICATORS.create("covariance", length=4).compute(
        frame(high, high=high, low=low)
    )["covariance"]
    assert out.iloc[:3].isna().all()  # first length-1 bars are warm-up
    assert np.isfinite(out.iloc[3])


def test_covariance_short_frame_all_nan():
    high = [1.0, 2.0, 3.0]
    low = [3.0, 2.0, 1.0]
    out = INDICATORS.create("covariance", length=5).compute(
        frame(high, high=high, low=low)
    )["covariance"]
    assert out.isna().all()


def test_covariance_flat_window_is_zero():
    # A constant high (zero variance) => zero covariance with anything.
    high = [7.0] * 10
    low = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    out = INDICATORS.create("covariance", length=4).compute(
        frame(high, high=high, low=low)
    )["covariance"]
    np.testing.assert_allclose(out.iloc[3:].to_numpy(), 0.0, atol=1e-12)


def test_covariance_perfectly_correlated_equals_variance():
    # When low == high, cov(high, low) == var(high) (sample, ddof=1).
    high = [10.0, 11.0, 9.0, 12.0, 8.0, 13.0, 7.0]
    out = INDICATORS.create("covariance", length=4).compute(
        frame(high, high=high, low=high)
    )["covariance"]
    var = (
        frame(high, high=high)["high"]
        .rolling(4, min_periods=4)
        .var(ddof=1)
    )
    np.testing.assert_allclose(
        out.dropna().to_numpy(), var.dropna().to_numpy(), atol=1e-12
    )


def test_covariance_anti_correlated_is_negative():
    # low moving opposite to high => negative covariance.
    high = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    low = [8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
    out = INDICATORS.create("covariance", length=5).compute(
        frame(high, high=high, low=low)
    )["covariance"]
    assert (out.dropna().to_numpy() < 0).all()


def test_covariance_ddof_zero_population_scaling():
    # ddof=0 is the population covariance: it equals the ddof=1 value scaled by (N-1)/N.
    f = deterministic_frame(80)
    n = 10
    sample = INDICATORS.create("covariance", length=n, ddof=1).compute(f)["covariance"]
    population = INDICATORS.create("covariance", length=n, ddof=0).compute(f)["covariance"]
    np.testing.assert_allclose(
        population.dropna().to_numpy(),
        sample.dropna().to_numpy() * (n - 1) / n,
        rtol=1e-9,
    )


def test_covariance_matches_pandas_oracle_on_walk():
    # Direct equality to the canonical pandas oracle on a realistic random walk.
    f = deterministic_frame(200)
    out = INDICATORS.create("covariance", length=30).compute(f)["covariance"]
    oracle = f["high"].rolling(30, min_periods=30).cov(f["low"])
    np.testing.assert_allclose(
        out.to_numpy(), oracle.to_numpy(), rtol=1e-12, atol=1e-12, equal_nan=True
    )


def test_covariance_output_shape_and_dtype():
    f = deterministic_frame(50)
    out = INDICATORS.create("covariance", length=30).compute(f)
    assert list(out.columns) == ["covariance"]
    assert out["covariance"].dtype == np.float64
    assert len(out) == len(f)
