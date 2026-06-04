"""Price transforms + Heikin-Ashi — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_hl2():
    f = frame([9.0, 11.0], high=[10.0, 12.0], low=[8.0, 10.0])
    np.testing.assert_allclose(INDICATORS.create("hl2").compute(f)["hl2"], [9.0, 11.0])


def test_hlc3():
    f = frame([9.0], high=[12.0], low=[6.0])  # (12+6+9)/3 = 9
    np.testing.assert_allclose(INDICATORS.create("hlc3").compute(f)["hlc3"], [9.0])


def test_ohlc4():
    f = frame([10.0], high=[12.0], low=[8.0], open_=[10.0])  # (10+12+8+10)/4 = 10
    np.testing.assert_allclose(INDICATORS.create("ohlc4").compute(f)["ohlc4"], [10.0])


def test_wcp():
    f = frame([10.0], high=[12.0], low=[8.0])  # (12+8+2*10)/4 = 10
    np.testing.assert_allclose(INDICATORS.create("wcp").compute(f)["wcp"], [10.0])


def test_midpoint():
    out = INDICATORS.create("midpoint", length=3).compute(frame([1.0, 5.0, 3.0, 8.0, 2.0]))["midpoint"]
    np.testing.assert_allclose(out.iloc[2], 3.0)  # (max5 + min1)/2
    np.testing.assert_allclose(out.iloc[4], 5.0)  # (max8 + min2)/2


def test_midprice():
    f = frame([1.0, 2.0, 3.0, 4.0, 5.0], high=[2.0, 4.0, 6.0, 8.0, 10.0], low=[0.0, 1.0, 2.0, 3.0, 4.0])
    out = INDICATORS.create("midprice", length=3).compute(f)["midprice"]
    np.testing.assert_allclose(out.iloc[2], 3.0)  # (max6 + min0)/2


def test_heikin_ashi():
    f = frame([10.0, 11.0, 12.0], high=[11.0, 12.0, 13.0], low=[9.0, 10.0, 11.0], open_=[10.0, 10.5, 11.0])
    out = INDICATORS.create("heikin_ashi").compute(f)
    ha_close = (np.array([10.0, 10.5, 11.0]) + np.array([11.0, 12.0, 13.0])
                + np.array([9.0, 10.0, 11.0]) + np.array([10.0, 11.0, 12.0])) / 4.0
    np.testing.assert_allclose(out["ha_close"], ha_close)
    assert out["ha_open"].iloc[0] == (10.0 + 10.0) / 2.0  # seed (open0 + close0)/2
    np.testing.assert_allclose(out["ha_open"].iloc[1], (out["ha_open"].iloc[0] + ha_close[0]) / 2.0)
    np.testing.assert_allclose(out["ha_high"].iloc[0], max(11.0, out["ha_open"].iloc[0], ha_close[0]))
