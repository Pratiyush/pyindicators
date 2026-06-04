"""Sub — closed-form (high - low) golden + edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.sub import sub  # noqa: F401  (fires @register)


def test_sub_closed_form_mixed_values():
    # Sub is exactly high - low pointwise.
    high = [5.0, 7.0, 9.0, 2.0, 0.0]
    low = [1.0, 2.0, 3.0, 1.0, -4.0]
    out = INDICATORS.create("sub").compute(frame([0.0] * 5, high=high, low=low))["sub"]
    expected = np.asarray(high, dtype="float64") - np.asarray(low, dtype="float64")
    np.testing.assert_array_equal(out.to_numpy(), expected)


def test_sub_equal_inputs_is_zero():
    # high == low everywhere -> range is exactly 0.0 on every bar.
    vals = [3.0, -2.0, 10.0, 0.0]
    out = INDICATORS.create("sub").compute(frame([0.0] * 4, high=vals, low=vals))["sub"]
    np.testing.assert_array_equal(out.to_numpy(), np.zeros(4))


def test_sub_no_warmup_and_length_dtype():
    # Pure transform: every bar is defined (no leading NaN) and length is preserved.
    df = frame([0.0, 0.0, 0.0], high=[2.0, 5.0, 9.0], low=[1.0, 3.0, 4.0])
    out = INDICATORS.create("sub").compute(df)["sub"]
    assert out.notna().all()
    assert len(out) == len(df)
    assert out.dtype == np.float64


def test_sub_single_row():
    out = INDICATORS.create("sub").compute(frame([0.0], high=[7.5], low=[2.5]))["sub"]
    assert out.to_numpy().tolist() == [5.0]


def test_sub_nan_propagates():
    df = pd.DataFrame(
        {"open": [1.0], "high": [np.nan], "low": [1.0], "close": [1.0], "volume": [1.0]}
    )
    out = INDICATORS.create("sub").compute(df)["sub"]
    assert np.isnan(out.iloc[0])


def test_sub_matches_numpy_on_random_walk():
    df = deterministic_frame(200)
    out = INDICATORS.create("sub").compute(df)["sub"]
    expected = df["high"].to_numpy() - df["low"].to_numpy()
    np.testing.assert_array_equal(out.to_numpy(), expected)


def test_sub_range_is_nonnegative_on_valid_ohlcv():
    # On real OHLCV high >= low, so the range (sub) is never negative.
    df = deterministic_frame(200)
    out = INDICATORS.create("sub").compute(df)["sub"]
    assert (out.to_numpy() >= 0.0).all()


def test_sub_rejects_unknown_param():
    # Params has extra="forbid": passing any parameter is a hard ValidationError.
    with pytest.raises(ValidationError):
        INDICATORS.create("sub", length=14)
