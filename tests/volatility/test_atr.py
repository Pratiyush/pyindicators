"""ATR — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_flat_market_is_zero():
    f = frame([5.0] * 20, high=[5.0] * 20, low=[5.0] * 20)
    out = INDICATORS.create("atr", length=5).compute(f)["atr"]
    np.testing.assert_allclose(out.iloc[5:], 0.0)


def test_constant_true_range():
    # H-L = 2, no gaps -> TR = 2 every bar -> ATR = 2 after the seed
    f = frame([10.0] * 20, high=[11.0] * 20, low=[9.0] * 20)
    out = INDICATORS.create("atr", length=5).compute(f)["atr"]
    np.testing.assert_allclose(out.iloc[4:], 2.0)


def test_short_frame_all_nan():
    assert INDICATORS.create("atr", length=14).compute(frame([1.0, 2.0]))["atr"].isna().all()
