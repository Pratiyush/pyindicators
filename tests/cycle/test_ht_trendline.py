"""HT_TRENDLINE — structural / golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS
from pyindicators.cycle._hilbert import LOOKBACK_63
from pyindicators.cycle.ht_trendline import ht_trendline  # noqa: F401 — registers @INDICATORS


def _series(df=None):
    df = deterministic_frame() if df is None else df
    return INDICATORS.create("ht_trendline").compute(df)["ht_trendline"]


def test_lookback_is_nan_then_finite():
    out = _series()
    assert out.iloc[:LOOKBACK_63].isna().all()
    assert out.iloc[LOOKBACK_63:].notna().all()


def test_output_shape_and_index_preserved():
    df = deterministic_frame()
    out = INDICATORS.create("ht_trendline").compute(df)
    assert list(out.columns) == ["ht_trendline"]
    assert out.index.equals(df.index)


def test_constant_series_equals_that_constant():
    # WMA(4) of SMA(const) of a flat price is the price itself (an overlay).
    df = deterministic_frame().assign(close=42.0)
    out = _series(df).dropna()
    np.testing.assert_allclose(out.to_numpy(), 42.0, atol=1e-9)


def test_trendline_tracks_price_level():
    # As a price overlay, the trendline stays in the price's neighbourhood, not near 0.
    df = deterministic_frame()
    out = _series(df).dropna().to_numpy()
    close = df["close"].to_numpy()
    assert out.min() >= close.min() * 0.5
    assert out.max() <= close.max() * 1.5


def test_functional_equals_registry():
    close = deterministic_frame()["close"]
    np.testing.assert_array_equal(
        ht_trendline(close).to_numpy(), _series().to_numpy()
    )
