"""Registry-driven meta-tests — run automatically over EVERY registered indicator, so a
new indicator is covered the moment it is added (zero per-indicator edits).

The crown jewel is ``test_no_lookahead_truncation_invariance``: an indicator is causal iff
its value at bar ``i`` depends only on rows ``0..i``, operationalised as
``compute(df).iloc[:k] == compute(df.iloc[:k])`` — broken by any centered window, negative
shift, full-series normalisation, or backfill.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from hypothesis import given

from ohlcv_gen import deterministic_frame, valid_ohlcv_frames
from pyindicators import INDICATORS, Indicator

NAMES = INDICATORS.names()
LONG = deterministic_frame()


def test_registry_nonempty():
    assert NAMES, "no indicators registered"


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_instantiable_with_defaults(name):
    ind = INDICATORS.create(name)
    assert isinstance(ind, Indicator)
    assert ind.name == name
    assert ind.outputs and len(set(ind.outputs)) == len(ind.outputs)


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
@given(df=valid_ohlcv_frames())
def test_shape_and_dtype_preserved(name, df):
    out = INDICATORS.create(name).compute(df)
    assert out.index.equals(df.index)
    assert len(out) == len(df)
    assert tuple(out.columns) == INDICATORS.get(name).spec.outputs
    assert all(str(dt) == "float64" for dt in out.dtypes)


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
@given(df=valid_ohlcv_frames())
def test_no_lookahead_truncation_invariance(name, df):
    ind = INDICATORS.create(name)
    if not ind.spec.causal:
        pytest.skip(f"{name} declares causal=False")
    full = ind.compute(df)
    n = len(df)
    for k in sorted({1, max(1, n // 2), n}):
        trunc = ind.compute(df.iloc[:k].copy())
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
    pd.testing.assert_frame_equal(df, before)


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_declared_bounds_respected(name):
    ind = INDICATORS.create(name)
    if not ind.spec.bounds:
        pytest.skip(f"{name} declares no bounds")
    out = ind.compute(LONG)
    for col, (lo, hi) in ind.spec.bounds.items():
        vals = out[col].to_numpy()
        finite = vals[np.isfinite(vals)]
        assert (finite >= lo - 1e-9).all(), f"{name}.{col} < {lo}: {finite.min()}"
        assert (finite <= hi + 1e-9).all(), f"{name}.{col} > {hi}: {finite.max()}"


# Indicators whose last row legitimately contains NaN by design:
#  - acos/asin: only defined on [-1,1]; NaN on price-scale input (TA-Lib behaves identically).
#  - hilo: the long/short sub-lines are complementary (only the active side has a value each bar).
_LAST_ROW_NAN_OK = {"acos", "asin", "hilo"}


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_last_row_finite_after_warmup(name):
    if name in _LAST_ROW_NAN_OK:
        pytest.skip(f"{name} has a by-design NaN in its last row (domain/complementary-band)")
    out = INDICATORS.create(name).compute(LONG)
    assert np.isfinite(out.iloc[-1].to_numpy()).all(), out.iloc[-1].to_dict()
