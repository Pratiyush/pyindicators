"""KST — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_constant_series_is_zero():
    out = INDICATORS.create("kst").compute(frame([5.0] * 100))
    np.testing.assert_allclose(out["kst"].dropna(), 0.0, atol=1e-9)  # ROCs all 0


def test_short_frame_all_nan():
    assert INDICATORS.create("kst").compute(frame([1.0] * 10))["kst"].isna().all()
