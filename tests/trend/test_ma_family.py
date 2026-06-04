"""VWMA, ZLMA, ALMA, FWMA, SINWMA, PWMA — golden + edge cases.

A constant series passes through any of these moving averages unchanged.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import frame
from pyindicators import INDICATORS

_CLOSE_MAS = ["zlma", "alma", "fwma", "sinwma", "pwma"]


@pytest.mark.parametrize("name", _CLOSE_MAS)
def test_ma_of_constant_is_constant(name):
    out = INDICATORS.create(name).compute(frame([7.0] * 80))
    np.testing.assert_allclose(out[name].dropna(), 7.0, atol=1e-9)


def test_vwma_constant_close():
    out = INDICATORS.create("vwma", length=5).compute(frame([7.0] * 12, volume=np.arange(1, 13.0)))
    np.testing.assert_allclose(out["vwma"].dropna(), 7.0)


def test_vwma_weights_by_volume():
    # close [10, 20], huge volume on the second bar -> VWMA near 20
    f = frame([10.0, 20.0], volume=[1.0, 1e6])
    out = INDICATORS.create("vwma", length=2).compute(f)["vwma"]
    assert out.iloc[1] > 19.9


@pytest.mark.parametrize("name", [*_CLOSE_MAS, "vwma"])
def test_short_frame_all_nan(name):
    assert INDICATORS.create(name).compute(frame([1.0, 2.0]))[name].isna().all()
