"""Lag — golden + edge cases.

There is no reference library for a bar delay: ``lag`` *is* ``pandas.Series.shift(length)``,
so the golden assertions compare directly against that closed form on hand-written and
deterministic data. Structural parity vs ``shift`` on real market data lives in the parity
suite (``tests/parity/test_parity_lag.py``).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.utils.lag import lag  # noqa: F401  (fires @register)


def test_golden_previous_close_default_length():
    # Default length=1: each bar carries the previous close; bar 0 is NaN (no prior bar).
    out = INDICATORS.create("lag").compute(frame([10.0, 11.0, 12.0, 13.0]))["lag"]
    assert np.isnan(out.iloc[0])
    np.testing.assert_array_equal(out.iloc[1:].to_numpy(), [10.0, 11.0, 12.0])


def test_golden_explicit_length_shifts_by_n():
    # length=2: value at bar i is close[i-2]; the first two bars are NaN.
    out = INDICATORS.create("lag", length=2).compute(frame([1.0, 2.0, 3.0, 4.0, 5.0]))["lag"]
    assert out.iloc[:2].isna().all()
    np.testing.assert_array_equal(out.iloc[2:].to_numpy(), [1.0, 2.0, 3.0])


def test_matches_pandas_shift_closed_form():
    # The whole definition is close.shift(length) — assert exact equality for several lengths.
    df = deterministic_frame(200)
    for length in (1, 3, 5, 21):
        out = INDICATORS.create("lag", length=length).compute(df)["lag"]
        expected = df["close"].shift(length)
        pd.testing.assert_series_equal(out, expected, check_names=False, check_exact=True)


def test_constant_series_is_constant_after_warmup():
    # A flat input shifts to itself: every non-warm-up bar equals the constant.
    out = INDICATORS.create("lag").compute(frame([7.0] * 10))["lag"]
    assert np.isnan(out.iloc[0])
    np.testing.assert_array_equal(out.iloc[1:].to_numpy(), np.full(9, 7.0))


def test_output_contract_and_dtype():
    out = INDICATORS.create("lag").compute(deterministic_frame(50))
    assert list(out.columns) == ["lag"]
    assert out["lag"].dtype == np.float64
    assert len(out) == 50


def test_short_frame_all_nan_when_length_exceeds_rows():
    # length >= number of rows -> nothing to borrow from -> entirely NaN, length preserved.
    out = INDICATORS.create("lag", length=5).compute(frame([1.0, 2.0, 3.0]))["lag"]
    assert len(out) == 3 and out.isna().all()


def test_single_bar_is_nan():
    one = INDICATORS.create("lag").compute(frame([42.0]))["lag"]
    assert len(one) == 1 and np.isnan(one.iloc[0])


def test_causal_truncation_invariance():
    # A backward shift is causal: computing on a prefix equals the prefix of the full result.
    df = deterministic_frame(120)
    full = INDICATORS.create("lag", length=3).compute(df)["lag"]
    for k in (1, 4, 60, 120):
        trunc = INDICATORS.create("lag", length=3).compute(df.iloc[:k].copy())["lag"]
        pd.testing.assert_series_equal(full.iloc[:k], trunc, check_exact=True)


def test_function_matches_registry():
    df = deterministic_frame(80)
    direct = lag(df["close"], length=4).to_numpy()
    viareg = INDICATORS.create("lag", length=4).compute(df)["lag"].to_numpy()
    np.testing.assert_array_equal(direct, viareg)


def test_rejects_zero_and_negative_length():
    import pytest

    # length <= 0 would look ahead (or be a no-op); Params (ge=1) forbids it.
    for bad in (0, -1):
        with pytest.raises(Exception):  # noqa: B017 (pydantic ValidationError on ge=1)
            INDICATORS.create("lag", length=bad)


def test_rejects_unknown_param():
    import pytest

    with pytest.raises(Exception):  # noqa: B017 (pydantic ValidationError on extra='forbid')
        INDICATORS.create("lag", window=3)


def test_empty_series():
    assert lag(pd.Series([], dtype="float64")).empty
