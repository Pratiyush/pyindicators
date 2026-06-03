"""Registry-driven meta-tests run automatically over EVERY registered indicator, so a
new indicator is covered the moment it is added — no per-indicator edits.

The crown jewel is `test_no_lookahead_truncation_invariance`: an indicator is causal iff
its value at bar ``i`` depends only on rows ``0..i``. We operationalize that as
truncation invariance — ``compute(df).iloc[:k] == compute(df.iloc[:k])`` — which any
look-ahead bug (centered window, negative shift, full-series normalization, bfill) breaks.
"""

from __future__ import annotations

import pandas as pd
import pytest
from hypothesis import given

from ohlcv_gen import valid_ohlcv_frames
from pyindicators import INDICATORS, Indicator

NAMES = INDICATORS.names()


def test_some_indicators_registered():
    assert len(NAMES) >= 28, NAMES


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_instantiable_with_defaults(name):
    ind = INDICATORS.create(name)
    assert isinstance(ind, Indicator)
    assert ind.name == name
    assert isinstance(ind.outputs, tuple) and ind.outputs
    assert len(set(ind.outputs)) == len(ind.outputs), "output names must be unique"


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
@given(df=valid_ohlcv_frames())
def test_shape_and_dtype_preserved(name, df):
    ind = INDICATORS.create(name)
    out = ind.compute(df)
    assert out.index.equals(df.index)
    assert len(out) == len(df)
    assert tuple(out.columns) == ind.outputs
    assert all(str(dt) == "float64" for dt in out.dtypes)


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
@given(df=valid_ohlcv_frames())
def test_no_lookahead_truncation_invariance(name, df):
    ind = INDICATORS.create(name)
    if not ind.causal:
        pytest.skip(f"{name} declares causal=False")
    full = ind.compute(df)
    n = len(df)
    cuts = {1, max(1, n // 2), n}
    for k in sorted(cuts):
        trunc = ind.compute(df.iloc[:k].copy())
        # NaN == NaN under assert_frame_equal; tolerances for float recurrences (ewm).
        pd.testing.assert_frame_equal(
            full.iloc[:k], trunc, check_exact=False, rtol=1e-9, atol=1e-12
        )


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
@given(df=valid_ohlcv_frames())
def test_deterministic_and_no_input_mutation(name, df):
    ind = INDICATORS.create(name)
    before = df.copy(deep=True)
    a = ind.compute(df)
    b = ind.compute(df)
    pd.testing.assert_frame_equal(a, b)
    pd.testing.assert_frame_equal(df, before)  # compute must not mutate its input
