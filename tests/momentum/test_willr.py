"""Williams %R — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_close_at_range_top_is_zero():
    c = np.arange(1, 30.0)
    out = INDICATORS.create("willr", length=14).compute(frame(c, high=c, low=c - 1))
    np.testing.assert_allclose(out["willr"].dropna().iloc[-5:], 0.0)


def test_flat_window_is_nan():
    out = INDICATORS.create("willr", length=14).compute(
        frame([5.0] * 40, high=[5.0] * 40, low=[5.0] * 40)
    )
    assert out["willr"].isna().all()
