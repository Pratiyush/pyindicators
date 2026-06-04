"""Linear Decay — golden values, closed-form structure, and edge cases.

Import the module directly so ``@INDICATORS.register`` fires for the parallel-build layout.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.utils import decay as decay_mod  # noqa: F401  (triggers registration)


def test_decay_golden_drop_then_floor():
    # length=5 -> step = 0.2. Row0 is seeded to close[0]. A spike to 10 then 0s decays
    # exactly one bar (10 -> 9.8) before the prior level falls below the floored 0.
    out = INDICATORS.create("decay", length=5).compute(frame([10.0, 0.0, 0.0, 0.0]))["decay"]
    np.testing.assert_allclose(out.to_numpy(), [10.0, 9.8, 0.0, 0.0], atol=1e-12)


def test_decay_constant_series_is_identity():
    # max(c, c - step, 0) == c for any c >= 0: a flat line decays to itself, every bar finite.
    c = np.full(20, 7.5)
    out = INDICATORS.create("decay", length=3).compute(frame(c))["decay"]
    np.testing.assert_allclose(out.to_numpy(), c, atol=1e-12)
    assert out.notna().all()


def test_decay_rides_rising_close():
    # On a strictly rising close the current bar always dominates close[t-1]-step, so the
    # line equals close exactly (after the seeded first bar, which is also close).
    c = np.arange(1.0, 11.0)
    out = INDICATORS.create("decay", length=5).compute(frame(c))["decay"]
    np.testing.assert_allclose(out.to_numpy(), c, atol=1e-12)


def test_decay_floors_at_zero():
    # A tiny prior close minus the step would go negative; the 0 column clamps it.
    out = INDICATORS.create("decay", length=10).compute(frame([0.05, 0.0, 0.0]))["decay"]
    np.testing.assert_allclose(out.to_numpy(), [0.05, 0.0, 0.0], atol=1e-12)


def test_decay_closed_form_structure_on_random_walk():
    # Definition: decay[i] == max(close[i], close[i-1] - 1/length, 0), seed decay[0]=max(c0,0).
    length = 5
    df = deterministic_frame(200)
    out = INDICATORS.create("decay", length=length).compute(df)["decay"].to_numpy()
    c = df["close"].to_numpy()
    prior = np.empty_like(c)
    prior[0] = c[0]
    prior[1:] = c[:-1] - 1.0 / length
    expected = np.maximum.reduce([c, prior, np.zeros_like(c)])
    np.testing.assert_allclose(out, expected, atol=1e-12)
    # Sanity: the line never drops below the current close and never goes negative.
    assert (out >= c - 1e-12).all()
    assert (out >= -1e-12).all()


def test_decay_no_warmup_nan():
    # Unlike windowed indicators, decay seeds row 0 and reads only one bar back -> all finite.
    out = INDICATORS.create("decay", length=5).compute(frame([3.0, 2.0, 4.0, 1.0]))["decay"]
    assert out.notna().all()


def test_decay_single_row():
    out = INDICATORS.create("decay", length=5).compute(frame([4.0]))["decay"]
    np.testing.assert_allclose(out.to_numpy(), [4.0], atol=1e-12)


def test_decay_length_one_step_is_one():
    # length=1 -> step 1.0: prior contributes close[t-1]-1.
    out = INDICATORS.create("decay", length=1).compute(frame([10.0, 0.0, 0.0]))["decay"]
    np.testing.assert_allclose(out.to_numpy(), [10.0, 9.0, 0.0], atol=1e-12)


def test_decay_nan_close_propagates():
    # A NaN close must yield NaN at that bar (not leak through the 0 floor column).
    c = pd.Series([5.0, np.nan, 3.0])
    out = decay_mod(c, length=5)  # decay_mod is the function (utils/__init__ re-exports it)
    assert np.isnan(out.iloc[1])
