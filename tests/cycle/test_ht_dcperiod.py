"""HT_DCPERIOD — structural / golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS
from pyindicators.cycle._hilbert import HT_START_32, LOOKBACK_32, hilbert_state, mask_lookback
from pyindicators.cycle.ht_dcperiod import ht_dcperiod  # noqa: F401 — registers @INDICATORS


def _series():
    return INDICATORS.create("ht_dcperiod").compute(deterministic_frame())["ht_dcperiod"]


def test_lookback_is_nan_then_finite():
    out = _series()
    assert out.iloc[:LOOKBACK_32].isna().all()
    assert out.iloc[LOOKBACK_32:].notna().all()


def test_output_shape_and_index_preserved():
    df = deterministic_frame()
    out = INDICATORS.create("ht_dcperiod").compute(df)
    assert list(out.columns) == ["ht_dcperiod"]
    assert out.index.equals(df.index)


def test_period_clamped_to_6_50():
    out = _series().dropna().to_numpy()
    assert out.min() >= 6.0 - 1e-9
    assert out.max() <= 50.0 + 1e-9


def test_constant_series_period_settles_within_clamp():
    # A flat price has no real cycle (detrend is identically 0, so the homodyne re/im
    # collapse and the period just carries forward). It must still stay inside the 6..50
    # clamp and settle to a single constant — a degenerate input outside parity coverage.
    df = deterministic_frame().assign(close=100.0)
    out = INDICATORS.create("ht_dcperiod").compute(df)["ht_dcperiod"].dropna().to_numpy()
    assert out.min() >= 6.0 - 1e-9
    assert out.max() <= 50.0 + 1e-9
    np.testing.assert_allclose(out[-1], out[-2], atol=1e-9)  # settled (constant tail)


def test_functional_equals_masked_state():
    close = deterministic_frame()["close"]
    expected = mask_lookback(
        hilbert_state(close, HT_START_32).smooth_period, LOOKBACK_32, close.index
    )
    np.testing.assert_array_equal(ht_dcperiod(close).to_numpy(), expected.to_numpy())
