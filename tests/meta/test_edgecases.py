"""Shared edge-case helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pyindicators.core import clamp, require_columns, safe_divide


def test_require_columns_ok_and_missing():
    df = pd.DataFrame({"close": [1.0]})
    require_columns(df, ("close",))  # no error
    with pytest.raises(ValueError):
        require_columns(df, ("high", "low"))


def test_safe_divide_series_numerator_and_zero_denominator():
    num = pd.Series([10.0, 20.0, 30.0])
    den = pd.Series([2.0, 0.0, 5.0])
    out = safe_divide(num, den)
    assert out.iloc[0] == 5.0
    assert np.isnan(out.iloc[1])  # division by zero -> fill (NaN)
    assert out.iloc[2] == 6.0


def test_safe_divide_scalar_numerator_and_custom_fill():
    den = pd.Series([2.0, 0.0, 4.0])
    out = safe_divide(100.0, den, fill=-1.0)
    assert out.iloc[0] == 50.0 and out.iloc[1] == -1.0 and out.iloc[2] == 25.0


def test_clamp():
    s = pd.Series([-2.0, 0.5, 2.0])
    assert clamp(s, -1.0, 1.0).tolist() == [-1.0, 0.5, 1.0]
