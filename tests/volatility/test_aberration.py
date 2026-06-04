"""Aberration — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_aberration_bands_ordered():
    out = INDICATORS.create("aberration").compute(deterministic_frame(120))
    m = out.dropna()
    assert (m["aber_sg"] >= m["aber_zg"]).all()  # upper >= middle >= lower
    assert (m["aber_zg"] >= m["aber_xg"]).all()
    assert (m["aber_atr"] >= 0).all()


def test_aberration_flat_has_zero_width():
    flat = np.full(40, 7.0)
    out = INDICATORS.create("aberration").compute(frame(flat, high=flat, low=flat))
    m = out.dropna()
    np.testing.assert_allclose(m["aber_sg"].to_numpy(), m["aber_zg"].to_numpy(), atol=1e-9)
    np.testing.assert_allclose(m["aber_atr"].to_numpy(), 0.0, atol=1e-9)


def test_aberration_short_frame_all_nan():
    out = INDICATORS.create("aberration").compute(frame([1.0, 2.0, 3.0]))
    assert out["aber_zg"].isna().all()
