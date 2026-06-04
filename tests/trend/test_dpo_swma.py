"""DPO + SWMA — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_dpo_constant_is_zero():
    out = INDICATORS.create("dpo", length=6).compute(frame([5.0] * 30))["dpo"]
    np.testing.assert_allclose(out.dropna(), 0.0, atol=1e-12)  # close == displaced SMA


def test_swma_constant_is_constant():
    out = INDICATORS.create("swma", length=5).compute(frame([7.0] * 12))["swma"]
    np.testing.assert_allclose(out.dropna(), 7.0)


def test_swma_symmetric_triangle_weights():
    # length 4 -> weights [1,2,2,1]/6 over [1,2,3,4] -> (1+4+6+4)/6 = 15/6
    out = INDICATORS.create("swma", length=4).compute(frame([1.0, 2.0, 3.0, 4.0]))["swma"]
    np.testing.assert_allclose(out.iloc[3], 15.0 / 6.0)
