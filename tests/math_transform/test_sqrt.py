"""Square Root — golden / closed-form + domain-guard edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.sqrt import sqrt  # noqa: F401  (import fires @register)


def test_sqrt_closed_form_perfect_squares():
    # sqrt of perfect squares is exact (no warm-up, every bar maps to its own value).
    out = INDICATORS.create("sqrt").compute(frame([0.0, 1.0, 4.0, 9.0, 16.0, 25.0]))["sqrt"]
    np.testing.assert_array_equal(out.to_numpy(), [0.0, 1.0, 2.0, 3.0, 4.0, 5.0])


def test_sqrt_matches_numpy_on_random_walk():
    df = deterministic_frame(200)
    out = INDICATORS.create("sqrt").compute(df)["sqrt"]
    np.testing.assert_allclose(out.to_numpy(), np.sqrt(df["close"].to_numpy()), rtol=0, atol=0)


def test_sqrt_negative_domain_is_nan():
    # Real square root is undefined on the negatives -> guarded to NaN (not a forced 0/complex).
    out = INDICATORS.create("sqrt").compute(frame([-4.0, -1.0, 0.0, 4.0]))["sqrt"]
    assert np.isnan(out.to_numpy()[:2]).all()
    np.testing.assert_array_equal(out.to_numpy()[2:], [0.0, 2.0])


def test_sqrt_propagates_nan():
    out = INDICATORS.create("sqrt").compute(frame([4.0, np.nan, 9.0]))["sqrt"]
    res = out.to_numpy()
    assert np.isnan(res[1])
    np.testing.assert_array_equal(res[[0, 2]], [2.0, 3.0])


def test_sqrt_length_and_dtype_preserved():
    # Output length == input length, float64, single 'sqrt' column, same index.
    df = frame([1.0, 2.0, 3.0])
    res = INDICATORS.create("sqrt").compute(df)
    assert list(res.columns) == ["sqrt"]
    assert res["sqrt"].dtype == np.float64
    assert len(res) == len(df)
    pd.testing.assert_index_equal(res.index, df.index)


def test_sqrt_short_frame_no_warmup():
    # No window => a single bar already has a value (unlike windowed indicators).
    out = INDICATORS.create("sqrt").compute(frame([16.0]))["sqrt"]
    assert out.notna().all()
    assert out.iloc[0] == 4.0


def test_sqrt_takes_no_params():
    # Parameter-free element-wise op: passing a param must be rejected by Params/contract.
    try:
        INDICATORS.create("sqrt", length=14)
    except (TypeError, ValueError):
        return
    raise AssertionError("sqrt should not accept parameters")
