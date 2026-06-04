"""NVI, PVI, PVOL, WAD — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_nvi_seeds_at_initial():
    out = INDICATORS.create("nvi").compute(deterministic_frame(60))["nvi"]
    assert out.iloc[0] == 1000.0  # seeded at the initial value


def test_nvi_changes_only_on_lower_volume():
    # volume strictly increasing -> NVI never changes from its seed
    f = frame([10.0, 11.0, 12.0, 13.0], volume=[1, 2, 3, 4])
    np.testing.assert_allclose(INDICATORS.create("nvi").compute(f)["nvi"], 1000.0)


def test_pvi_changes_only_on_higher_volume():
    # volume strictly decreasing -> PVI never changes from its seed
    f = frame([10.0, 11.0, 12.0, 13.0], volume=[4, 3, 2, 1])
    np.testing.assert_allclose(INDICATORS.create("pvi").compute(f)["pvi"], 1000.0)


def test_pvol_is_close_times_volume():
    f = frame([10.0, 20.0], volume=[3.0, 4.0])
    np.testing.assert_allclose(INDICATORS.create("pvol").compute(f)["pvol"], [30.0, 80.0])


def test_wad_accumulates_on_up_closes():
    f = frame([10.0, 11.0, 12.0], high=[10.5, 11.5, 12.5], low=[9.5, 10.5, 11.5])
    out = INDICATORS.create("wad").compute(f)["wad"]
    assert out.iloc[0] == 0.0 and out.iloc[-1] > 0  # rising closes accumulate
