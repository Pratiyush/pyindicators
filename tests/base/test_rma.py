"""RMA (Wilder smoothing) — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_constant_series():
    out = INDICATORS.create("rma", length=3).compute(frame([4.0] * 10))
    assert out["rma"].iloc[:2].isna().all()
    np.testing.assert_allclose(out["rma"].iloc[2:], 4.0)


def test_seed_is_sma_then_wilder_recurrence():
    c = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    out = INDICATORS.create("rma", length=3).compute(frame(c))
    seed = np.mean(c[:3])  # 2.0 at index 2
    assert out["rma"].iloc[2] == seed
    nxt = (seed * 2 + c[3]) / 3  # Wilder: prev*(n-1)/n + x/n
    np.testing.assert_allclose(out["rma"].iloc[3], nxt)


def test_short_frame_is_all_nan():
    assert INDICATORS.create("rma", length=10).compute(frame([1.0, 2.0]))["rma"].isna().all()
