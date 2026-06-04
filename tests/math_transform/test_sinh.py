"""sinh — closed-form golden values + edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.math_transform.sinh import sinh  # noqa: F401  (registers @INDICATORS)


def test_sinh_closed_form_small_values():
    # sinh is exact and element-wise; check against numpy on a finite, small range.
    close = np.array([-2.0, -0.5, 0.0, 0.5, 1.0, 3.0])
    out = INDICATORS.create("sinh").compute(frame(close))["sinh"]
    np.testing.assert_allclose(out.to_numpy(), np.sinh(close), rtol=0, atol=1e-12)


def test_sinh_zero_and_oddness():
    # sinh(0) == 0 exactly, and sinh is odd: sinh(-x) == -sinh(x).
    close = np.array([-1.5, -0.25, 0.0, 0.25, 1.5])
    out = INDICATORS.create("sinh").compute(frame(close))["sinh"].to_numpy()
    assert out[2] == 0.0
    np.testing.assert_allclose(out, -out[::-1], rtol=0, atol=1e-15)


def test_sinh_constant_window_is_constant():
    # A flat series maps to a flat output (no warm-up, no smoothing).
    out = INDICATORS.create("sinh").compute(frame([0.7] * 6))["sinh"]
    np.testing.assert_allclose(out.to_numpy(), np.sinh(0.7), rtol=0, atol=1e-12)
    assert not out.isna().any()


def test_sinh_short_frame_no_warmup():
    # Single bar still produces a value (stateless transform, length == input length).
    out = INDICATORS.create("sinh").compute(frame([1.25]))["sinh"]
    assert out.shape == (1,)
    np.testing.assert_allclose(out.to_numpy(), [np.sinh(1.25)], rtol=0, atol=1e-12)


def test_sinh_nan_propagates():
    out = INDICATORS.create("sinh").compute(frame([0.5, np.nan, -0.5]))["sinh"]
    assert np.isnan(out.to_numpy()[1])
    assert np.isfinite(out.to_numpy()[[0, 2]]).all()


def test_sinh_large_value_overflows_to_inf():
    # Unbounded transform: huge inputs legitimately overflow to +inf (matches TA-Lib C sinh).
    with np.errstate(over="ignore"):
        out = INDICATORS.create("sinh").compute(frame([800.0]))["sinh"]
    assert np.isinf(out.to_numpy()[0]) and out.to_numpy()[0] > 0


def test_sinh_output_contract():
    out = INDICATORS.create("sinh").compute(frame([0.1, 0.2, 0.3]))
    assert list(out.columns) == ["sinh"]
    assert out["sinh"].dtype == np.float64
    assert len(out) == 3


def test_sinh_preserves_index():
    idx = pd.RangeIndex(start=5, stop=8)
    df = frame([0.1, 0.2, 0.3])
    df.index = idx
    out = INDICATORS.create("sinh").compute(df)
    assert out.index.equals(idx)
