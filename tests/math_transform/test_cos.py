"""COS (vector trigonometric cosine) — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.cos import cos  # noqa: F401  (import fires @register)


def test_cos_closed_form_known_angles():
    # cos(0)=1, cos(pi/2)=0, cos(pi)=-1, cos(2pi)=1 — exact reference values.
    angles = [0.0, np.pi / 2.0, np.pi, 1.5 * np.pi, 2.0 * np.pi]
    out = INDICATORS.create("cos").compute(frame(angles))["cos"]
    np.testing.assert_allclose(out.to_numpy(), np.cos(np.asarray(angles)), atol=1e-12)


def test_cos_matches_numpy_on_random_walk():
    df = deterministic_frame(300)
    out = INDICATORS.create("cos").compute(df)["cos"]
    np.testing.assert_allclose(out.to_numpy(), np.cos(df["close"].to_numpy()), rtol=0, atol=0)


def test_cos_constant_input_is_constant():
    # A flat close -> a single repeated cosine value (no window, no drift).
    out = INDICATORS.create("cos").compute(frame([2.0, 2.0, 2.0, 2.0]))["cos"]
    np.testing.assert_allclose(out.to_numpy(), np.full(4, np.cos(2.0)), atol=1e-12)


def test_cos_short_frame_no_warmup():
    # Pointwise transform: even a 1-row frame yields a finite value (no NaN warm-up).
    out = INDICATORS.create("cos").compute(frame([0.0]))["cos"]
    assert out.notna().all()
    np.testing.assert_allclose(out.to_numpy(), [1.0], atol=1e-12)


def test_cos_nan_propagates():
    out = INDICATORS.create("cos").compute(frame([0.0, np.nan, np.pi]))["cos"]
    assert np.isnan(out.to_numpy()[1])
    np.testing.assert_allclose(out.to_numpy()[[0, 2]], [1.0, -1.0], atol=1e-12)


def test_cos_output_contract():
    df = frame([0.1, 0.2, 0.3])
    res = INDICATORS.create("cos").compute(df)
    assert list(res.columns) == ["cos"]
    assert len(res) == len(df)
    assert res["cos"].dtype == np.float64
