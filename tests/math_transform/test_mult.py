"""Vector Arithmetic Mult — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.mult import mult  # noqa: F401  (import fires @register)


def test_mult_closed_form_hand_checked():
    # Each bar is exactly high*low (no warm-up, every bar maps to its own two inputs).
    df = frame([1.0, 1.0, 1.0, 1.0], high=[2.0, 3.0, 4.0, 5.0], low=[10.0, 20.0, 30.0, 40.0])
    out = INDICATORS.create("mult").compute(df)["mult"]
    np.testing.assert_array_equal(out.to_numpy(), [20.0, 60.0, 120.0, 200.0])


def test_mult_matches_numpy_on_random_walk():
    df = deterministic_frame(200)
    out = INDICATORS.create("mult").compute(df)["mult"]
    expected = df["high"].to_numpy() * df["low"].to_numpy()
    np.testing.assert_allclose(out.to_numpy(), expected, rtol=0, atol=0)


def test_mult_propagates_nan():
    # NaN in either operand -> NaN at that bar; finite bars are exact.
    df = frame([1.0, 1.0, 1.0], high=[2.0, np.nan, 4.0], low=[5.0, 6.0, np.nan])
    res = INDICATORS.create("mult").compute(df)["mult"].to_numpy()
    assert np.isnan(res[1]) and np.isnan(res[2])
    assert res[0] == 10.0


def test_mult_handles_signs_and_zero():
    # Pure multiplication is total: sign rules apply and any zero factor zeros the bar.
    df = frame([1.0, 1.0, 1.0, 1.0], high=[-2.0, -2.0, 0.0, 3.0], low=[3.0, -4.0, 9.0, 0.0])
    out = INDICATORS.create("mult").compute(df)["mult"]
    np.testing.assert_array_equal(out.to_numpy(), [-6.0, 8.0, 0.0, 0.0])


def test_mult_length_and_dtype_preserved():
    # Output length == input length, float64, single 'mult' column, same index.
    df = frame([1.0, 2.0, 3.0], high=[4.0, 5.0, 6.0], low=[7.0, 8.0, 9.0])
    res = INDICATORS.create("mult").compute(df)
    assert list(res.columns) == ["mult"]
    assert res["mult"].dtype == np.float64
    assert len(res) == len(df)
    pd.testing.assert_index_equal(res.index, df.index)


def test_mult_short_frame_no_warmup():
    # No window => a single bar already has a value (unlike windowed indicators).
    out = INDICATORS.create("mult").compute(frame([1.0], high=[6.0], low=[7.0]))["mult"]
    assert out.notna().all()
    assert out.iloc[0] == 42.0


def test_mult_takes_no_params():
    # Parameter-free element-wise op: passing a param must be rejected by the contract.
    try:
        INDICATORS.create("mult", length=14)
    except (TypeError, ValueError):
        return
    raise AssertionError("mult should not accept parameters")
