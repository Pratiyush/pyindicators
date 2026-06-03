"""Donchian Channels — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_rising_channel():
    c = np.arange(1, 30.0)
    out = INDICATORS.create("donchian", lower_length=5, upper_length=5).compute(
        frame(c, high=c, low=c)
    )
    np.testing.assert_allclose(out["dc_upper"].iloc[-1], c[-1])  # highest = current
    np.testing.assert_allclose(out["dc_lower"].iloc[-1], c[-5])  # lowest = 5 bars back
    np.testing.assert_allclose(out["dc_middle"].iloc[-1], (c[-1] + c[-5]) / 2)


def test_short_frame_all_nan():
    out = INDICATORS.create("donchian").compute(frame([1.0, 2.0]))
    assert out["dc_upper"].isna().all()
