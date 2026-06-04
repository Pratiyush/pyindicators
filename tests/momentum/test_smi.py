"""SMI Ergodic — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_smi_osc_is_line_minus_signal():
    out = INDICATORS.create("smi").compute(deterministic_frame(120))
    np.testing.assert_allclose(
        out["smi_osc"].to_numpy(),
        (out["smi"] - out["smi_signal"]).to_numpy(),
        equal_nan=True,
    )


def test_smi_bounds():
    out = INDICATORS.create("smi").compute(deterministic_frame(200))
    for col in ("smi", "smi_signal"):
        v = out[col].dropna().to_numpy()
        assert v.min() >= -1.0 - 1e-9 and v.max() <= 1.0 + 1e-9


def test_smi_flat_is_nan():
    out = INDICATORS.create("smi").compute(frame([5.0] * 80))["smi"]
    assert out.isna().all()  # zero |momentum| -> undefined
