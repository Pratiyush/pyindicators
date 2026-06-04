"""log10 (base-10 logarithm) — golden / closed-form + domain edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.math_transform.log10 import log10  # noqa: F401  (fires @register)


def test_log10_exact_powers_of_ten():
    # Closed form: log10(10**k) == k exactly.
    f = frame([1.0, 10.0, 100.0, 1000.0, 10000.0])
    out = INDICATORS.create("log10").compute(f)["log10"]
    np.testing.assert_allclose(out.to_numpy(), [0.0, 1.0, 2.0, 3.0, 4.0], atol=1e-12)


def test_log10_matches_numpy_on_positive_domain():
    c = np.array([0.5, 2.5, 7.0, 42.0, 123.456])
    out = INDICATORS.create("log10").compute(frame(c))["log10"]
    np.testing.assert_allclose(out.to_numpy(), np.log10(c), rtol=1e-12)


def test_log10_constant_series_is_flat():
    out = INDICATORS.create("log10").compute(frame([50.0, 50.0, 50.0]))["log10"]
    np.testing.assert_allclose(out.to_numpy(), np.full(3, np.log10(50.0)), rtol=1e-12)


def test_log10_zero_and_negative_are_nan():
    # Out-of-domain inputs -> NaN (guarded), positives still resolve.
    out = INDICATORS.create("log10").compute(frame([10.0, 0.0, -5.0, 100.0]))["log10"]
    v = out.to_numpy()
    assert np.isnan(v[1]) and np.isnan(v[2])  # log10(0) and log10(-5) undefined
    np.testing.assert_allclose([v[0], v[3]], [1.0, 2.0], atol=1e-12)


def test_log10_preserves_nan():
    out = INDICATORS.create("log10").compute(frame([10.0, np.nan, 100.0]))["log10"]
    v = out.to_numpy()
    assert np.isnan(v[1])
    np.testing.assert_allclose([v[0], v[2]], [1.0, 2.0], atol=1e-12)


def test_log10_output_contract():
    f = frame([1.0, 10.0, 100.0])
    out = INDICATORS.create("log10").compute(f)
    assert list(out.columns) == ["log10"]
    assert len(out) == len(f)
    assert out["log10"].dtype == np.float64


def test_log10_single_bar():
    out = INDICATORS.create("log10").compute(frame([1000.0]))["log10"]
    np.testing.assert_allclose(out.to_numpy(), [3.0], atol=1e-12)
