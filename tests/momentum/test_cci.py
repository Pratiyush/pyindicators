"""CCI — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_flat_typical_price_is_zero():
    f = frame([5.0] * 12, high=[5.0] * 12, low=[5.0] * 12)
    out = INDICATORS.create("cci", length=5).compute(f)["cci"]
    np.testing.assert_allclose(out.iloc[4:], 0.0)  # MAD == 0 guarded to 0


def test_finite_on_trend():
    out = INDICATORS.create("cci", length=5).compute(frame(np.arange(1, 20.0)))["cci"]
    assert np.isfinite(out.iloc[-1])
