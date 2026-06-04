"""FLOOR — golden / closed-form + edge cases (round toward -inf, NaN-preserving)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.floor import floor  # noqa: F401  (fires @register)


def test_floor_golden_values():
    # Closed form: floor rounds toward negative infinity, integers map to themselves.
    closes = [1.2, -1.2, 2.7, -2.7, 3.0, -3.0, 0.0, -0.4]
    expected = [1.0, -2.0, 2.0, -3.0, 3.0, -3.0, 0.0, -1.0]
    out = INDICATORS.create("floor").compute(frame(closes))["floor"]
    np.testing.assert_array_equal(out.to_numpy(), np.array(expected))


def test_floor_equals_numpy_floor_on_walk():
    df = deterministic_frame(200)
    out = INDICATORS.create("floor").compute(df)["floor"]
    np.testing.assert_array_equal(out.to_numpy(), np.floor(df["close"].to_numpy()))


def test_floor_preserves_nan_and_no_warmup():
    # No window => zero warm-up; NaN passes straight through (never fabricated).
    closes = [np.nan, 5.9, np.nan, -0.1]
    out = INDICATORS.create("floor").compute(frame(closes))["floor"]
    assert np.isnan(out.iloc[0]) and np.isnan(out.iloc[2])
    assert out.iloc[1] == 5.0 and out.iloc[3] == -1.0
    assert out.notna().sum() == 2  # only the two finite inputs produce values


def test_floor_already_integer_is_identity():
    closes = [10.0, -7.0, 0.0, 42.0]
    out = INDICATORS.create("floor").compute(frame(closes))["floor"]
    np.testing.assert_array_equal(out.to_numpy(), np.array(closes))


def test_floor_constant_flat_series():
    out = INDICATORS.create("floor").compute(frame([3.3] * 6))["floor"]
    assert (out == 3.0).all()


def test_floor_single_row_short_frame():
    out = INDICATORS.create("floor").compute(frame([2.999]))["floor"]
    assert len(out) == 1 and out.iloc[0] == 2.0


def test_floor_output_contract():
    df = deterministic_frame(50)
    out = INDICATORS.create("floor").compute(df)
    assert list(out.columns) == ["floor"]
    assert len(out) == len(df)
    assert out["floor"].dtype == np.float64
    assert out.index.equals(df.index)


def test_floor_takes_no_params():
    # Stateless transform: passing a parameter must be rejected by the contract.
    with pytest.raises(TypeError):
        INDICATORS.create("floor", length=14)


def test_floor_le_close_and_within_one():
    # Defining property: floor(x) <= x < floor(x) + 1 for every finite bar.
    c = pd.Series(deterministic_frame(120)["close"].to_numpy())
    f = INDICATORS.create("floor").compute(frame(c.to_numpy()))["floor"]
    assert (f <= c).all()
    assert ((c - f) < 1.0).all()
