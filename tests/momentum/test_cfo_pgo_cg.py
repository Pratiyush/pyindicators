"""CFO, PGO, CG — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_cfo_constant_is_zero():
    out = INDICATORS.create("cfo", length=5).compute(frame([5.0] * 20))["cfo"]
    np.testing.assert_allclose(out.dropna(), 0.0, atol=1e-9)  # price == its own forecast


def test_pgo_finite_and_flat_nan():
    assert np.isfinite(INDICATORS.create("pgo").compute(deterministic_frame(60))["pgo"].iloc[-1])
    flat = frame([5.0] * 30, high=[5.0] * 30, low=[5.0] * 30)
    assert INDICATORS.create("pgo").compute(flat)["pgo"].isna().all()  # ATR 0 -> guarded


def test_cg_finite_on_real_data():
    assert np.isfinite(INDICATORS.create("cg").compute(deterministic_frame(60))["cg"].iloc[-1])
