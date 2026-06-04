"""+DI/-DI/DX/ADXR, CHOP, VHF, QStick — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_di_family_in_uptrend():
    c = np.arange(1, 140.0)
    f = frame(c, high=c + 0.5, low=c - 0.5)
    pdi = INDICATORS.create("plus_di").compute(f)["plus_di"].iloc[-1]
    mdi = INDICATORS.create("minus_di").compute(f)["minus_di"].iloc[-1]
    assert pdi > mdi  # uptrend -> +DI dominates
    assert np.isfinite(INDICATORS.create("dx").compute(f)["dx"].iloc[-1])
    assert np.isfinite(INDICATORS.create("adxr").compute(f)["adxr"].iloc[-1])


def test_chop_finite_and_flat_nan():
    assert np.isfinite(INDICATORS.create("chop").compute(deterministic_frame(100))["chop"].iloc[-1])
    flat = frame([5.0] * 40, high=[5.0] * 40, low=[5.0] * 40)
    assert INDICATORS.create("chop").compute(flat)["chop"].isna().all()


def test_vhf_finite_and_flat_nan():
    assert np.isfinite(INDICATORS.create("vhf").compute(deterministic_frame(100))["vhf"].iloc[-1])
    assert INDICATORS.create("vhf").compute(frame([5.0] * 60))["vhf"].isna().all()


def test_qstick_bullish_when_close_above_open():
    f = frame([10.0, 11.0, 12.0], open_=[9.0, 10.0, 11.0])
    assert INDICATORS.create("qstick", length=2).compute(f)["qstick"].iloc[-1] > 0
