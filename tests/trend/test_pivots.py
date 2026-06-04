"""Pivot Points — closed-form golden + edge cases.

No smoothing or seeding is involved, so every value is checked against the explicit
floor-trader formula on the PRIOR bar. The indicator must be strictly causal (first row
NaN) and must reduce sensibly on a flat bar.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.pivots import pivots  # noqa: F401 — ensures @register fires


def test_pivots_closed_form_two_bars():
    # Prior bar: H=12, L=8, C=11 -> P=(12+8+11)/3 = 31/3. Levels project onto bar #2.
    f = frame([11.0, 10.0], high=[12.0, 13.0], low=[8.0, 9.0])
    out = INDICATORS.create("pivots").compute(f)
    h, low_, c = 12.0, 8.0, 11.0
    p = (h + low_ + c) / 3.0
    rng = h - low_
    row = out.iloc[1]
    assert np.isclose(row["pivot"], p)
    assert np.isclose(row["r1"], 2.0 * p - low_)
    assert np.isclose(row["s1"], 2.0 * p - h)
    assert np.isclose(row["r2"], p + rng)
    assert np.isclose(row["s2"], p - rng)
    assert np.isclose(row["r3"], h + 2.0 * (p - low_))
    assert np.isclose(row["s3"], low_ - 2.0 * (h - p))


def test_pivots_first_bar_all_nan():
    # No predecessor -> every output undefined on the first row.
    out = INDICATORS.create("pivots").compute(frame([10.0, 11.0, 12.0]))
    assert out.iloc[0].isna().all()
    assert out.iloc[1:].notna().all().all()


def test_pivots_columns_and_length():
    df = deterministic_frame(50)
    out = INDICATORS.create("pivots").compute(df)
    assert list(out.columns) == ["pivot", "r1", "s1", "r2", "s2", "r3", "s3"]
    assert len(out) == len(df)
    assert (out.dtypes == np.float64).all()


def test_pivots_flat_prior_bar_collapses_to_pivot():
    # Prior bar fully flat (H==L==C==5) -> range 0 -> all levels equal the pivot == 5.
    f = frame([5.0, 7.0], high=[5.0, 9.0], low=[5.0, 6.0])
    row = INDICATORS.create("pivots").compute(f).iloc[1]
    assert np.allclose(row.to_numpy(), 5.0)


def test_pivots_ordering_when_close_in_range():
    # With a normal prior bar the supports sit below P and resistances above it, ordered.
    f = frame([20.0, 21.0], high=[22.0, 23.0], low=[18.0, 19.0])
    row = INDICATORS.create("pivots").compute(f).iloc[1]
    assert row["s3"] < row["s2"] < row["s1"] < row["pivot"] < row["r1"] < row["r2"] < row["r3"]


def test_pivots_is_causal_independent_of_future():
    # Changing only the LAST bar must not alter any earlier pivot row (no look-ahead).
    base = deterministic_frame(40)
    bumped = base.copy()
    bumped.iloc[-1, :] = bumped.iloc[-1, :] * 1.5
    a = INDICATORS.create("pivots").compute(base).iloc[:-1]
    b = INDICATORS.create("pivots").compute(bumped).iloc[:-1]
    np.testing.assert_allclose(a.to_numpy(), b.to_numpy())


def test_pivots_takes_no_params():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):  # Params has extra="forbid"
        INDICATORS.create("pivots", length=5)
