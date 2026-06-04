"""Vector Arithmetic Div — golden / closed-form + zero-denominator guard edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.div import div  # noqa: F401  (import fires @register)


def test_div_closed_form_exact():
    # Pointwise high/low is exact (no warm-up, every bar maps to its own quotient).
    df = frame([1.0, 1.0, 1.0], high=[10.0, 9.0, 8.0], low=[2.0, 3.0, 4.0])
    out = INDICATORS.create("div").compute(df)["div"]
    np.testing.assert_array_equal(out.to_numpy(), [5.0, 3.0, 2.0])


def test_div_matches_numpy_ratio_on_random_walk():
    df = deterministic_frame(200)
    out = INDICATORS.create("div").compute(df)["div"]
    expected = df["high"].to_numpy() / df["low"].to_numpy()
    np.testing.assert_allclose(out.to_numpy(), expected, rtol=0, atol=0)


def test_div_zero_denominator_is_nan():
    # safe_divide guards low == 0 to NaN (vs TA-Lib's inf) per CONVENTIONS.md; non-zero rows
    # are unaffected.
    df = frame([1.0, 1.0, 1.0], high=[5.0, 7.0, 9.0], low=[0.0, 2.0, 0.0])
    out = INDICATORS.create("div").compute(df)["div"].to_numpy()
    assert np.isnan(out[[0, 2]]).all()
    assert out[1] == 3.5


def test_div_propagates_nan_in_either_input():
    df = frame([1.0, 1.0, 1.0], high=[6.0, np.nan, 8.0], low=[2.0, 4.0, np.nan])
    out = INDICATORS.create("div").compute(df)["div"].to_numpy()
    assert np.isnan(out[[1, 2]]).all()
    assert out[0] == 3.0


def test_div_length_and_dtype_preserved():
    # Output length == input length, float64, single 'div' column, same index.
    df = frame([1.0, 2.0, 3.0], high=[4.0, 5.0, 6.0], low=[2.0, 2.5, 3.0])
    res = INDICATORS.create("div").compute(df)
    assert list(res.columns) == ["div"]
    assert res["div"].dtype == np.float64
    assert len(res) == len(df)
    pd.testing.assert_index_equal(res.index, df.index)


def test_div_short_frame_no_warmup():
    # No window => a single bar already has a value (unlike windowed indicators).
    df = frame([1.0], high=[12.0], low=[4.0])
    out = INDICATORS.create("div").compute(df)["div"]
    assert out.notna().all()
    assert out.iloc[0] == 3.0


def test_div_takes_no_params():
    # Parameter-free element-wise op: passing a param must be rejected by the contract.
    try:
        INDICATORS.create("div", length=14)
    except (TypeError, ValueError):
        return
    raise AssertionError("div should not accept parameters")
