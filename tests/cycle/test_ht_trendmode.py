"""HT_TRENDMODE — structural / golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS
from pyindicators.cycle._hilbert import HT_START_63, LOOKBACK_63, hilbert_state, mask_lookback
from pyindicators.cycle.ht_trendmode import ht_trendmode  # noqa: F401 — registers @INDICATORS


def _series(df=None):
    df = deterministic_frame() if df is None else df
    return INDICATORS.create("ht_trendmode").compute(df)["ht_trendmode"]


def test_lookback_is_nan_then_finite():
    out = _series()
    assert out.iloc[:LOOKBACK_63].isna().all()
    assert out.iloc[LOOKBACK_63:].notna().all()


def test_output_shape_and_index_preserved():
    df = deterministic_frame()
    out = INDICATORS.create("ht_trendmode").compute(df)
    assert list(out.columns) == ["ht_trendmode"]
    assert out.index.equals(df.index)


def test_output_is_binary_zero_or_one():
    # The regime flag is strictly 0 or 1 (and within the declared (0, 1) bounds).
    out = _series().dropna().to_numpy()
    assert set(np.unique(out)).issubset({0.0, 1.0})
    assert out.min() >= 0.0
    assert out.max() <= 1.0


def test_both_regimes_appear_on_deterministic_frame():
    # A random-walk frame visits both trending and cycling regimes — guards against a
    # constant-flag bug.
    out = _series().dropna().to_numpy()
    assert (out == 0.0).any()
    assert (out == 1.0).any()


def test_functional_equals_masked_state():
    close = deterministic_frame()["close"]
    expected = mask_lookback(
        hilbert_state(close, HT_START_63).trend_mode, LOOKBACK_63, close.index
    )
    np.testing.assert_array_equal(ht_trendmode(close).to_numpy(), expected.to_numpy())


def test_functional_equals_registry():
    close = deterministic_frame()["close"]
    np.testing.assert_array_equal(ht_trendmode(close).to_numpy(), _series().to_numpy())
