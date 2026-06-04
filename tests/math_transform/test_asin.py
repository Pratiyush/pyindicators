"""ASIN (arcsine math transform) — golden / closed-form + domain edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS

# Direct import so @INDICATORS.register fires for this standalone test module.
from pyindicators.math_transform.asin import asin  # noqa: F401


def test_asin_closed_form_known_angles():
    # asin of the canonical sines -> the exact angles (radians).
    x = [-1.0, -np.sqrt(3) / 2, -0.5, 0.0, 0.5, np.sqrt(2) / 2, 1.0]
    expected = [-np.pi / 2, -np.pi / 3, -np.pi / 6, 0.0, np.pi / 6, np.pi / 4, np.pi / 2]
    out = INDICATORS.create("asin").compute(frame(x))["asin"]
    np.testing.assert_allclose(out.to_numpy(), expected, atol=1e-12)


def test_asin_matches_numpy_arcsin_in_domain():
    x = np.linspace(-1.0, 1.0, 101)
    out = INDICATORS.create("asin").compute(frame(x))["asin"]
    np.testing.assert_allclose(out.to_numpy(), np.arcsin(x), atol=1e-12)


def test_asin_out_of_domain_is_nan():
    # |x| > 1 is undefined -> NaN (never clamped/fabricated); in-domain entries survive.
    x = [-2.0, -1.5, 0.25, 1.5, 100.0]
    out = INDICATORS.create("asin").compute(frame(x))["asin"]
    assert np.isnan(out.iloc[0]) and np.isnan(out.iloc[1])
    np.testing.assert_allclose(out.iloc[2], np.arcsin(0.25), atol=1e-12)
    assert np.isnan(out.iloc[3]) and np.isnan(out.iloc[4])


def test_asin_endpoints_are_half_pi():
    out = INDICATORS.create("asin").compute(frame([-1.0, 1.0]))["asin"]
    np.testing.assert_allclose(out.to_numpy(), [-np.pi / 2, np.pi / 2], atol=1e-12)


def test_asin_constant_flat_series():
    # A flat in-domain series maps to a flat angle (no warm-up, exact per-bar transform).
    out = INDICATORS.create("asin").compute(frame([0.5, 0.5, 0.5, 0.5]))["asin"]
    np.testing.assert_allclose(out.to_numpy(), np.full(4, np.pi / 6), atol=1e-12)


def test_asin_is_odd_function():
    x = np.array([0.1, 0.37, 0.6, 0.95])
    pos = INDICATORS.create("asin").compute(frame(x))["asin"].to_numpy()
    neg = INDICATORS.create("asin").compute(frame(-x))["asin"].to_numpy()
    np.testing.assert_allclose(neg, -pos, atol=1e-12)


def test_asin_short_single_row():
    out = INDICATORS.create("asin").compute(frame([0.0]))["asin"]
    assert out.shape == (1,)
    np.testing.assert_allclose(out.to_numpy(), [0.0], atol=1e-12)


def test_asin_length_dtype_and_columns():
    out_df = INDICATORS.create("asin").compute(frame([0.0, 0.5, -0.5]))
    assert list(out_df.columns) == ["asin"]
    assert out_df["asin"].dtype == np.float64
    assert len(out_df) == 3
