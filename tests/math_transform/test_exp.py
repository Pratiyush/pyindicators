"""EXP — golden / closed-form + edge cases (element-wise ``e ** close``)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.exp import exp  # noqa: F401  (import fires @register)


def test_exp_closed_form_known_points():
    # exp(0)=1, exp(1)=e, exp(2)=e**2, exp(-1)=1/e. The transform has no warm-up.
    out = INDICATORS.create("exp").compute(frame([0.0, 1.0, 2.0, -1.0]))["exp"]
    expected = np.array([1.0, np.e, np.e**2, 1.0 / np.e])
    np.testing.assert_allclose(out.to_numpy(), expected, rtol=1e-12, atol=0.0)


def test_exp_matches_numpy_on_random_walk():
    df = deterministic_frame(200)
    out = INDICATORS.create("exp").compute(df)["exp"]
    np.testing.assert_allclose(out.to_numpy(), np.exp(df["close"].to_numpy()), rtol=1e-12)


def test_exp_no_warmup_full_length_and_finite():
    # A per-bar transform yields one value per row with no leading NaNs.
    df = frame([1.0, 2.0, 3.0])
    out = INDICATORS.create("exp").compute(df)["exp"]
    assert len(out) == 3
    assert out.notna().all()
    assert out.name == "exp"


def test_exp_constant_series_is_constant():
    out = INDICATORS.create("exp").compute(frame([2.0, 2.0, 2.0, 2.0]))["exp"]
    np.testing.assert_allclose(out.to_numpy(), np.full(4, np.e**2), rtol=1e-12)


def test_exp_nan_propagates():
    out = INDICATORS.create("exp").compute(frame([0.0, np.nan, 1.0]))["exp"]
    assert np.isnan(out.iloc[1])
    np.testing.assert_allclose(out.iloc[[0, 2]].to_numpy(), [1.0, np.e], rtol=1e-12)


def test_exp_strictly_positive_and_monotonic():
    # exp is strictly increasing and > 0 everywhere it is defined.
    out = INDICATORS.create("exp").compute(frame([-3.0, -1.0, 0.0, 2.0, 5.0]))["exp"]
    v = out.to_numpy()
    assert (v > 0).all()
    assert np.all(np.diff(v) > 0)


def test_exp_single_row():
    out = INDICATORS.create("exp").compute(frame([3.5]))["exp"]
    np.testing.assert_allclose(out.to_numpy(), [np.exp(3.5)], rtol=1e-12)
