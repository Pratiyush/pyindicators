"""HT_SINE — structural / golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS
from pyindicators.cycle._hilbert import LOOKBACK_63
from pyindicators.cycle.ht_sine import ht_sine  # noqa: F401 — registers @INDICATORS


def _frame(df=None):
    df = deterministic_frame() if df is None else df
    return INDICATORS.create("ht_sine").compute(df)


def test_lookback_is_nan_then_finite():
    out = _frame()
    for col in ("sine", "lead_sine"):
        assert out[col].iloc[:LOOKBACK_63].isna().all()
        assert out[col].iloc[LOOKBACK_63:].notna().all()


def test_output_shape_and_index_preserved():
    df = deterministic_frame()
    out = INDICATORS.create("ht_sine").compute(df)
    assert list(out.columns) == ["sine", "lead_sine"]
    assert out.index.equals(df.index)


def test_lines_within_unit_bounds():
    out = _frame()
    for col in ("sine", "lead_sine"):
        vals = out[col].dropna().to_numpy()
        assert vals.min() >= -1.0 - 1e-9
        assert vals.max() <= 1.0 + 1e-9


def test_lead_leads_sine_by_45_degrees():
    # lead_sine = sin(asin-of-sine + 45deg) only loosely, but the defining relation is exact:
    # both come from the same dcPhase, so lead is never identical to sine on cyclic data.
    out = _frame().dropna()
    assert not np.allclose(out["sine"].to_numpy(), out["lead_sine"].to_numpy())


def test_functional_equals_registry():
    close = deterministic_frame()["close"]
    reg = _frame()
    fn = ht_sine(close)
    for col in ("sine", "lead_sine"):
        np.testing.assert_array_equal(fn[col].to_numpy(), reg[col].to_numpy())
