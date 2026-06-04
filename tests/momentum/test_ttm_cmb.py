"""TTM Momentum + Composite Index — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_ttm_momentum_constant_is_zero():
    flat = frame([5.0] * 40, high=[5.0] * 40, low=[5.0] * 40)
    out = INDICATORS.create("ttm_momentum", length=10).compute(flat)["ttm_momentum"]
    np.testing.assert_allclose(out.dropna(), 0.0, atol=1e-9)  # close == midline


def test_ttm_momentum_finite_on_real_data():
    out = INDICATORS.create("ttm_momentum").compute(deterministic_frame(80))["ttm_momentum"]
    assert np.isfinite(out.iloc[-1])


def test_cmb_composite_finite_on_real_data():
    out = INDICATORS.create("cmb_composite_index").compute(deterministic_frame(80))
    assert np.isfinite(out["cmb_composite_index"].iloc[-1])


def test_cmb_composite_flat_is_nan():
    out = INDICATORS.create("cmb_composite_index").compute(frame([5.0] * 60))["cmb_composite_index"]
    assert out.isna().all()  # flat -> RSI NaN -> composite NaN
