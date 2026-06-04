"""HT_PHASOR — structural / golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS
from pyindicators.cycle._hilbert import HT_START_32, LOOKBACK_32, hilbert_state, mask_lookback
from pyindicators.cycle.ht_phasor import ht_phasor  # noqa: F401 — registers @INDICATORS


def _frame():
    return INDICATORS.create("ht_phasor").compute(deterministic_frame())


def test_output_shape_and_index_preserved():
    df = deterministic_frame()
    out = INDICATORS.create("ht_phasor").compute(df)
    assert list(out.columns) == ["in_phase", "quadrature"]
    assert out.index.equals(df.index)


def test_lookback_is_nan_then_finite():
    out = _frame()
    for col in ("in_phase", "quadrature"):
        assert out[col].iloc[:LOOKBACK_32].isna().all()
        assert out[col].iloc[LOOKBACK_32:].notna().all()


def test_components_are_distinct():
    # In-phase (a pure 3-bar delay of the detrender) and quadrature (the FIR of the
    # detrender) are different signals — guard against accidentally emitting one twice.
    out = _frame().dropna()
    assert not np.allclose(out["in_phase"].to_numpy(), out["quadrature"].to_numpy())


def test_constant_series_components_vanish():
    # A flat price has no oscillation: the detrender is identically 0, so both phasor
    # components collapse to 0 — a degenerate input outside parity coverage.
    df = deterministic_frame().assign(close=100.0)
    out = INDICATORS.create("ht_phasor").compute(df).dropna()
    np.testing.assert_allclose(out["in_phase"].to_numpy(), 0.0, atol=1e-9)
    np.testing.assert_allclose(out["quadrature"].to_numpy(), 0.0, atol=1e-9)


def test_functional_equals_masked_state():
    close = deterministic_frame()["close"]
    state = hilbert_state(close, HT_START_32)
    expected_in = mask_lookback(state.in_phase, LOOKBACK_32, close.index)
    expected_q = mask_lookback(state.quadrature, LOOKBACK_32, close.index)
    got = ht_phasor(close)
    np.testing.assert_array_equal(got["in_phase"].to_numpy(), expected_in.to_numpy())
    np.testing.assert_array_equal(got["quadrature"].to_numpy(), expected_q.to_numpy())
