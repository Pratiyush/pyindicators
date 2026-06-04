"""cosh — closed-form (numpy.cosh) + edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.cosh import cosh  # noqa: F401  (import fires @register)


def test_cosh_matches_numpy_closed_form():
    df = deterministic_frame(200)
    out = INDICATORS.create("cosh").compute(df)["cosh"]
    np.testing.assert_allclose(out.to_numpy(), np.cosh(df["close"].to_numpy()), rtol=0, atol=0)


def test_cosh_small_known_values():
    # cosh(0) == 1, and the function is symmetric: cosh(-x) == cosh(x).
    out = INDICATORS.create("cosh").compute(frame([0.0, 1.0, -1.0, 2.0, -2.0]))["cosh"]
    expected = np.array([1.0, np.cosh(1.0), np.cosh(1.0), np.cosh(2.0), np.cosh(2.0)])
    np.testing.assert_allclose(out.to_numpy(), expected, rtol=1e-12, atol=0)


def test_cosh_is_at_least_one_and_no_warmup():
    # Defined on all reals: every bar is populated (no NaN warm-up) and cosh >= 1.
    out = INDICATORS.create("cosh").compute(deterministic_frame(120))["cosh"]
    assert out.notna().all()
    assert (out.to_numpy() >= 1.0 - 1e-12).all()


def test_cosh_constant_series_is_flat():
    out = INDICATORS.create("cosh").compute(frame([3.0, 3.0, 3.0, 3.0]))["cosh"]
    np.testing.assert_allclose(out.to_numpy(), np.cosh(3.0), rtol=1e-12, atol=0)


def test_cosh_single_row():
    out = INDICATORS.create("cosh").compute(frame([0.5]))["cosh"]
    assert out.shape == (1,)
    np.testing.assert_allclose(out.to_numpy(), [np.cosh(0.5)], rtol=1e-12, atol=0)


def test_cosh_propagates_nan():
    out = cosh(pd.Series([0.0, np.nan, 1.0]))
    assert np.isnan(out.to_numpy()[1])
    np.testing.assert_allclose(out.to_numpy()[[0, 2]], [1.0, np.cosh(1.0)], rtol=1e-12, atol=0)


def test_cosh_output_contract():
    out = INDICATORS.create("cosh").compute(deterministic_frame(50))
    assert list(out.columns) == ["cosh"]
    assert str(out["cosh"].dtype) == "float64"
    assert len(out) == 50
