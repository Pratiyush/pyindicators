"""FAMA — structural / golden + edge cases (the slow MAMA companion line)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.fama import fama  # noqa: F401 — import so @register fires
from pyindicators.trend.mama import _LOOKBACK


def test_single_output_named_fama():
    df = deterministic_frame()
    out = INDICATORS.create("fama").compute(df)
    assert list(out.columns) == ["fama"]
    assert out.index.equals(df.index)


def test_lookback_is_nan_then_finite():
    out = INDICATORS.create("fama").compute(deterministic_frame())["fama"]
    assert out.iloc[:_LOOKBACK].isna().all()
    assert out.iloc[_LOOKBACK:].notna().all()


def test_short_frame_all_nan():
    out = INDICATORS.create("fama").compute(deterministic_frame(20))["fama"]
    assert out.isna().all()


def test_empty_series():
    assert fama(pd.Series([], dtype="float64")).empty


def test_constant_series_settles_to_constant_on_tail():
    # the seeded EMA (prev = 0 at bar 6) climbs toward the flat price and settles on the tail.
    vals = INDICATORS.create("fama").compute(frame([7.5] * 200))["fama"].dropna().to_numpy()
    assert (vals <= 7.5 + 1e-9).all()
    np.testing.assert_allclose(vals[-50:], 7.5, atol=1e-6)


def test_nan_close_propagates():
    close = deterministic_frame()["close"].copy()
    close.iloc[150] = np.nan
    assert fama(close).iloc[150:].isna().all()


def test_fama_equals_mama_second_output():
    # FAMA must be exactly the second line of the shared MAMA recurrence.
    df = deterministic_frame()
    mama_out = INDICATORS.create("mama").compute(df)["fama"]
    fama_out = INDICATORS.create("fama").compute(df)["fama"]
    np.testing.assert_array_equal(mama_out.to_numpy(), fama_out.to_numpy())


def test_functional_matches_registry():
    df = deterministic_frame()
    reg = INDICATORS.create("fama").compute(df)["fama"]
    np.testing.assert_array_equal(fama(df["close"]).to_numpy(), reg.to_numpy())
