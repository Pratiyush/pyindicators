"""Market Facilitation Index — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_value():
    f = frame([10.0], high=[12.0], low=[8.0], volume=[2.0])  # (12-8)/2 = 2
    np.testing.assert_allclose(INDICATORS.create("marketfi").compute(f)["marketfi"].iloc[0], 2.0)


def test_zero_volume_is_nan():
    f = frame([10.0, 10.0], high=[12.0, 12.0], low=[8.0, 8.0], volume=[0.0, 0.0])
    assert INDICATORS.create("marketfi").compute(f)["marketfi"].isna().all()
