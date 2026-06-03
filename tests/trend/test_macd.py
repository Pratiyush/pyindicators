"""MACD — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_constant_series_is_zero():
    out = INDICATORS.create("macd").compute(frame([7.0] * 60))
    np.testing.assert_allclose(out["macd"].dropna(), 0.0, atol=1e-12)
    np.testing.assert_allclose(out["macd_signal"].dropna(), 0.0, atol=1e-12)
    np.testing.assert_allclose(out["macd_hist"].dropna(), 0.0, atol=1e-12)


def test_outputs_present_and_finite():
    out = INDICATORS.create("macd").compute(frame(np.arange(1, 100.0)))
    assert list(out.columns) == ["macd", "macd_signal", "macd_hist"]
    assert np.isfinite(out.iloc[-1].to_numpy()).all()
