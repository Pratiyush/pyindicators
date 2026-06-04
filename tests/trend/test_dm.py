"""+DM / -DM / Aroon Oscillator — golden + edge cases."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


@pytest.mark.parametrize("name", ["plus_dm", "minus_dm"])
def test_dm_constant_is_zero(name):
    # no high/low movement -> no directional movement -> 0 after the warm-up
    out = INDICATORS.create(name, length=14).compute(frame([5.0] * 60))[name]
    np.testing.assert_allclose(out.dropna().to_numpy(), 0.0, atol=1e-12)


def test_plus_dm_positive_on_rising_highs():
    f = frame(np.arange(1.0, 41.0), high=np.arange(1.5, 41.5), low=np.arange(0.5, 40.5))
    out = INDICATORS.create("plus_dm", length=14).compute(f)["plus_dm"]
    assert (out.dropna() > 0).all()  # steady up-moves accumulate +DM


def test_minus_dm_positive_on_falling_lows():
    f = frame(np.arange(40.0, 0.0, -1.0), high=np.arange(40.5, 0.5, -1.0),
              low=np.arange(39.5, -0.5, -1.0))
    out = INDICATORS.create("minus_dm", length=14).compute(f)["minus_dm"]
    assert (out.dropna() > 0).all()  # steady down-moves accumulate -DM


@pytest.mark.parametrize("name", ["plus_dm", "minus_dm", "aroon_osc"])
def test_dm_short_frame_all_nan(name):
    assert INDICATORS.create(name).compute(frame([1.0, 2.0, 3.0]))[name].isna().all()


def test_aroon_osc_matches_aroon_component():
    f = deterministic_frame(120)
    osc = INDICATORS.create("aroon_osc", length=25).compute(f)["aroon_osc"]
    ref = INDICATORS.create("aroon", length=25).compute(f)["aroon_osc"]
    np.testing.assert_allclose(osc.to_numpy(), ref.to_numpy(), equal_nan=True)


def test_aroon_osc_plus_100_on_strict_uptrend():
    f = frame(np.arange(1.0, 60.0), high=np.arange(1.0, 60.0), low=np.arange(1.0, 60.0))
    out = INDICATORS.create("aroon_osc", length=25).compute(f)["aroon_osc"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 100.0)  # HH always freshest
