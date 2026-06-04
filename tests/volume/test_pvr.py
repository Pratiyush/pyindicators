"""Price Volume Rank — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_pvr_classification():
    f = frame([10.0, 11.0, 12.0, 11.0], volume=[100, 200, 150, 100])
    out = INDICATORS.create("pvr").compute(f)["pvr"]
    assert np.isnan(out.iloc[0])  # no prior bar
    assert out.iloc[1] == 1.0  # price up, volume up
    assert out.iloc[2] == 2.0  # price up, volume down
    assert out.iloc[3] == 4.0  # price down, volume down
