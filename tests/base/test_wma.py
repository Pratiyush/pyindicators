"""WMA — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_known_value():
    # WMA(3) of [1,2,3] = (1*1 + 2*2 + 3*3) / (1+2+3) = 14/6
    out = INDICATORS.create("wma", length=3).compute(frame([1.0, 2.0, 3.0]))
    assert out["wma"].iloc[:2].isna().all()
    np.testing.assert_allclose(out["wma"].iloc[2], 14.0 / 6.0)


def test_constant_series():
    out = INDICATORS.create("wma", length=4).compute(frame([5.0] * 8))
    np.testing.assert_allclose(out["wma"].iloc[3:], 5.0)


def test_short_frame_is_all_nan():
    assert INDICATORS.create("wma", length=10).compute(frame([1.0, 2.0]))["wma"].isna().all()
