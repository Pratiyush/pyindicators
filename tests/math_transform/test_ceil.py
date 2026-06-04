"""Ceil — closed-form (numpy.ceil) golden + edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.ceil import ceil  # noqa: F401  (fires @register)


def test_ceil_closed_form_mixed_signs():
    # Ceiling is exactly numpy.ceil pointwise: round each value toward +inf.
    close = [1.2, -2.7, 3.0, 0.0, -0.4, 5.9, 2.5, -1.0]
    out = INDICATORS.create("ceil").compute(frame(close))["ceil"]
    np.testing.assert_array_equal(out.to_numpy(), np.ceil(np.asarray(close, dtype="float64")))


def test_ceil_integers_unchanged():
    close = [-3.0, -1.0, 0.0, 2.0, 10.0, 100.0]
    out = INDICATORS.create("ceil").compute(frame(close))["ceil"]
    np.testing.assert_array_equal(out.to_numpy(), np.asarray(close, dtype="float64"))


def test_ceil_no_warmup_and_length_dtype():
    # Pure transform: every bar is defined (no leading NaN) and length is preserved.
    df = frame([0.1, 9.9, -4.2])
    out = INDICATORS.create("ceil").compute(df)["ceil"]
    assert out.notna().all()
    assert len(out) == len(df)
    assert out.dtype == np.float64


def test_ceil_constant_series_is_flat():
    out = INDICATORS.create("ceil").compute(frame([4.0] * 6))["ceil"]
    np.testing.assert_array_equal(out.to_numpy(), np.full(6, 4.0))


def test_ceil_single_row():
    out = INDICATORS.create("ceil").compute(frame([7.3]))["ceil"]
    assert out.to_numpy().tolist() == [8.0]


def test_ceil_nan_propagates():
    df = pd.DataFrame(
        {"open": [1.0], "high": [1.0], "low": [1.0], "close": [np.nan], "volume": [1.0]}
    )
    out = INDICATORS.create("ceil").compute(df)["ceil"]
    assert np.isnan(out.iloc[0])


def test_ceil_matches_numpy_on_random_walk():
    df = deterministic_frame(200)
    out = INDICATORS.create("ceil").compute(df)["ceil"]
    np.testing.assert_array_equal(out.to_numpy(), np.ceil(df["close"].to_numpy()))


def test_ceil_rejects_unknown_param():
    # Params has extra="forbid": passing any parameter is a hard ValidationError.
    with pytest.raises(ValidationError):
        INDICATORS.create("ceil", length=14)
