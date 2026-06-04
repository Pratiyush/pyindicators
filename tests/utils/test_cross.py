"""crossover / crossunder / crossany / cross_value — golden + pandas-ta parity."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import real_frame
from pyindicators.base import sma
from pyindicators.utils import cross_value, crossany, crossover, crossunder


def test_crossover_golden():
    a = pd.Series([1.0, 1.0, 3.0, 3.0])
    b = pd.Series([2.0, 2.0, 2.0, 2.0])
    np.testing.assert_array_equal(crossover(a, b).to_numpy(), [0.0, 0.0, 1.0, 0.0])


def test_crossunder_golden():
    a = pd.Series([3.0, 3.0, 1.0, 1.0])
    b = pd.Series([2.0, 2.0, 2.0, 2.0])
    np.testing.assert_array_equal(crossunder(a, b).to_numpy(), [0.0, 0.0, 1.0, 0.0])


def test_crossany_is_either_direction():
    a = pd.Series([1.0, 3.0, 1.0])  # up-cross at 1, down-cross at 2
    b = pd.Series([2.0, 2.0, 2.0])
    np.testing.assert_array_equal(crossany(a, b).to_numpy(), [0.0, 1.0, 1.0])


def test_cross_value_above_and_below():
    s = pd.Series([20.0, 40.0, 20.0])  # crosses 30 up at 1, down at 2
    np.testing.assert_array_equal(cross_value(s, 30.0, above=True).to_numpy(), [0.0, 1.0, 0.0])
    np.testing.assert_array_equal(cross_value(s, 30.0, above=False).to_numpy(), [0.0, 0.0, 1.0])


def test_cross_parity_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    c = real_frame()["close"]
    fast, slow = sma(c, 10), sma(c, 30)
    # Compare only where both inputs (and their priors) are finite. pandas-ta builds the
    # "below" case as ``~current & ~previous``; during the NaN warmup ``a > b`` is False so
    # ``~False`` makes it spuriously emit 1.0. Our crossunder is strict (``(a<b) & (prev a>prev b)``)
    # and correctly emits 0 in the warmup, so parity is asserted on the post-warmup region only.
    valid = (fast.notna() & slow.notna() & fast.shift(1).notna() & slow.shift(1).notna()).to_numpy()
    np.testing.assert_array_equal(
        crossover(fast, slow).to_numpy()[valid],
        pta.cross(fast, slow, above=True).to_numpy().astype(float)[valid],
    )
    np.testing.assert_array_equal(
        crossunder(fast, slow).to_numpy()[valid],
        pta.cross(fast, slow, above=False).to_numpy().astype(float)[valid],
    )
    cv_valid = c.notna().to_numpy()
    np.testing.assert_array_equal(
        cross_value(c, 100.0, above=True).to_numpy()[cv_valid],
        pta.cross_value(c, 100.0, above=True).to_numpy().astype(float)[cv_valid],
    )
