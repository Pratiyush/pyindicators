"""tanh — golden / closed-form + edge cases."""

from __future__ import annotations

import math

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.tanh import tanh  # noqa: F401  (import fires @register)


def test_tanh_closed_form():
    # Element-wise: out == tanh(close) exactly, against math.tanh value-by-value.
    vals = [-3.0, -1.0, -0.25, 0.0, 0.5, 1.0, 2.0, 5.0]
    out = INDICATORS.create("tanh").compute(frame(vals))["tanh"].to_numpy()
    np.testing.assert_allclose(out, [math.tanh(v) for v in vals], rtol=0.0, atol=1e-12)


def test_tanh_known_anchors():
    # tanh(0)=0, tanh(1)=0.76159415595..., odd symmetry tanh(-x) = -tanh(x).
    out = INDICATORS.create("tanh").compute(frame([0.0, 1.0, -1.0]))["tanh"].to_numpy()
    assert out[0] == 0.0
    np.testing.assert_allclose(out[1], 0.7615941559557649, rtol=0.0, atol=1e-15)
    np.testing.assert_allclose(out[2], -out[1], rtol=0.0, atol=1e-15)


def test_tanh_within_bounds():
    # Never escapes the inclusive [-1, 1] bound declared in the spec (float64 saturates to
    # +/-1 exactly for large |x|, which is why the mathematically-open interval is asserted
    # inclusively here).
    df = deterministic_frame(400)
    df = df.assign(close=df["close"] - df["close"].mean())  # large magnitudes -> tail
    out = INDICATORS.create("tanh").compute(df)["tanh"].to_numpy()
    assert np.all(out >= -1.0) and np.all(out <= 1.0)


def test_tanh_strict_interval_for_small_inputs():
    # For modest |x| it stays strictly inside (-1, 1) (no premature clamping).
    out = INDICATORS.create("tanh").compute(frame([-2.0, -0.5, 0.0, 0.5, 2.0]))["tanh"].to_numpy()
    assert np.all(out > -1.0) and np.all(out < 1.0)


def test_tanh_saturates_at_extremes():
    # Large inputs map to ~+/-1; +/-inf map exactly to +/-1.
    out = INDICATORS.create("tanh").compute(frame([50.0, -50.0, np.inf, -np.inf]))["tanh"]
    a = out.to_numpy()
    np.testing.assert_allclose(a[0], 1.0, atol=1e-12)
    np.testing.assert_allclose(a[1], -1.0, atol=1e-12)
    assert a[2] == 1.0 and a[3] == -1.0


def test_tanh_constant_series():
    # Flat input -> flat tanh of that constant (no warm-up, every bar defined).
    out = INDICATORS.create("tanh").compute(frame([2.0] * 6))["tanh"].to_numpy()
    np.testing.assert_allclose(out, math.tanh(2.0), rtol=0.0, atol=1e-12)


def test_tanh_nan_propagates_no_shift():
    # Zero lookback: NaN stays in place, finite neighbours are untouched (no shift).
    out = INDICATORS.create("tanh").compute(frame([1.0, np.nan, 2.0]))["tanh"].to_numpy()
    assert np.isnan(out[1])
    np.testing.assert_allclose([out[0], out[2]], [math.tanh(1.0), math.tanh(2.0)], atol=1e-12)


def test_tanh_short_frame_all_defined():
    # No window, so even a single bar is fully defined (no NaN warm-up).
    out = INDICATORS.create("tanh").compute(frame([0.3]))["tanh"]
    assert out.notna().all()
    np.testing.assert_allclose(out.to_numpy(), [math.tanh(0.3)], atol=1e-12)


def test_tanh_length_and_dtype():
    df = deterministic_frame(50)
    out = INDICATORS.create("tanh").compute(df)
    assert list(out.columns) == ["tanh"]
    assert len(out) == len(df)
    assert out["tanh"].dtype == np.float64
