"""Volume SMA + Relative Volume — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_vol_sma_constant():
    out = INDICATORS.create("vol_sma", length=5).compute(frame([5.0] * 12, volume=[100.0] * 12))
    np.testing.assert_allclose(out["vol_sma"].dropna(), 100.0)


def test_rvol_constant_is_one():
    out = INDICATORS.create("rvol", length=5).compute(frame([5.0] * 12, volume=[100.0] * 12))
    np.testing.assert_allclose(out["rvol"].dropna(), 1.0)


def test_rvol_spike_above_average():
    v = [100.0] * 9 + [500.0]
    out = INDICATORS.create("rvol", length=5).compute(frame([5.0] * 10, volume=v))["rvol"]
    assert out.iloc[-1] > 1.5  # a volume spike vs the trailing average
