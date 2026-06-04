"""HT_DCPHASE — structural / golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS
from pyindicators.cycle._hilbert import LOOKBACK_63
from pyindicators.cycle.ht_dcphase import ht_dcphase  # noqa: F401 — registers @INDICATORS


def _series(df=None):
    df = deterministic_frame() if df is None else df
    return INDICATORS.create("ht_dcphase").compute(df)["ht_dcphase"]


def test_lookback_is_nan_then_finite():
    out = _series()
    assert out.iloc[:LOOKBACK_63].isna().all()
    assert out.iloc[LOOKBACK_63:].notna().all()


def test_output_shape_and_index_preserved():
    df = deterministic_frame()
    out = INDICATORS.create("ht_dcphase").compute(df)
    assert list(out.columns) == ["ht_dcphase"]
    assert out.index.equals(df.index)


def test_phase_in_wrapped_degree_range():
    # TA-Lib wraps anything above 315 down by 360, so the phase sits in (-45, 315].
    out = _series().dropna().to_numpy()
    assert out.min() > -45.0 - 1e-6
    assert out.max() <= 315.0 + 1e-6


def test_functional_equals_registry():
    close = deterministic_frame()["close"]
    np.testing.assert_array_equal(ht_dcphase(close).to_numpy(), _series().to_numpy())
