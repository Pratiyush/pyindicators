"""SIN — golden / closed-form + edge cases (element-wise trigonometric sine)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS

# Direct import so @INDICATORS.register fires even before the coordinator wires the package.
from pyindicators.math_transform.sin import sin  # noqa: F401


def test_sin_closed_form_known_angles():
    # sin at the textbook angles: 0, pi/2, pi, 3pi/2, 2pi -> 0, 1, 0, -1, 0.
    angles = [0.0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi]
    out = INDICATORS.create("sin").compute(frame(angles))["sin"]
    np.testing.assert_allclose(out.to_numpy(), [0.0, 1.0, 0.0, -1.0, 0.0], atol=1e-12)


def test_sin_matches_numpy_on_random_walk():
    df = deterministic_frame(200)
    out = INDICATORS.create("sin").compute(df)["sin"]
    np.testing.assert_allclose(out.to_numpy(), np.sin(df["close"].to_numpy()), rtol=0, atol=0)


def test_sin_is_bounded_pm_one():
    out = INDICATORS.create("sin").compute(deterministic_frame(300))["sin"].to_numpy()
    finite = out[np.isfinite(out)]
    assert finite.size > 0
    assert (finite >= -1.0).all() and (finite <= 1.0).all()


def test_sin_no_warmup_full_length_no_nan_for_finite_input():
    # Pure transform: every finite input maps to a finite output (no leading NaN warm-up).
    df = frame([0.5, 1.0, 1.5, 2.0, 2.5])
    out = INDICATORS.create("sin").compute(df)["sin"]
    assert len(out) == len(df)
    assert out.notna().all()


def test_sin_constant_series_is_flat():
    # A flat input yields a flat output equal to sin(constant).
    out = INDICATORS.create("sin").compute(frame([1.0] * 6))["sin"]
    np.testing.assert_allclose(out.to_numpy(), np.full(6, np.sin(1.0)), atol=1e-12)


def test_sin_propagates_nan():
    df = frame([0.0, np.nan, np.pi / 2])
    out = INDICATORS.create("sin").compute(df)["sin"]
    assert np.isnan(out.iloc[1])
    np.testing.assert_allclose(out.iloc[[0, 2]].to_numpy(), [0.0, 1.0], atol=1e-12)


def test_sin_odd_symmetry():
    # sin(-x) == -sin(x): negate the input, expect the negated output.
    xs = [0.3, 1.2, 2.7, 4.1]
    pos = INDICATORS.create("sin").compute(frame(xs))["sin"].to_numpy()
    neg = INDICATORS.create("sin").compute(frame([-x for x in xs]))["sin"].to_numpy()
    np.testing.assert_allclose(neg, -pos, atol=1e-12)


def test_sin_single_row():
    out = INDICATORS.create("sin").compute(frame([np.pi / 2]))["sin"]
    assert len(out) == 1
    np.testing.assert_allclose(out.to_numpy(), [1.0], atol=1e-12)
