"""MA Spread — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_constant_is_zero():
    out = INDICATORS.create("ma_spread", fast=3, slow=6).compute(frame([5.0] * 20))["ma_spread"]
    np.testing.assert_allclose(out.iloc[5:], 0.0, atol=1e-12)


def test_uptrend_fast_above_slow():
    out = INDICATORS.create("ma_spread", fast=3, slow=6).compute(frame(np.arange(1, 30.0)))
    assert (out["ma_spread"].dropna() > 0).all()  # rising -> fast SMA above slow SMA
