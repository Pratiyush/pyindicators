"""True Range — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_first_bar_falls_back_to_high_low():
    f = frame([10.0, 11.0], high=[10.5, 12.0], low=[9.5, 10.5])
    tr = INDICATORS.create("true_range").compute(f)["true_range"]
    assert tr.iloc[0] == 1.0  # 10.5 - 9.5 (no prior close)


def test_gap_uses_previous_close():
    # bar1: H=12, L=10.5, prevC=10 -> max(1.5, |12-10|=2, |10.5-10|=0.5) = 2
    f = frame([10.0, 11.0], high=[10.5, 12.0], low=[9.5, 10.5])
    tr = INDICATORS.create("true_range").compute(f)["true_range"]
    np.testing.assert_allclose(tr.iloc[1], 2.0)


def test_flat_no_gap_is_zero():
    f = frame([5.0, 5.0, 5.0], high=[5.0, 5.0, 5.0], low=[5.0, 5.0, 5.0])
    np.testing.assert_allclose(
        INDICATORS.create("true_range").compute(f)["true_range"].to_numpy(), [0.0, 0.0, 0.0]
    )
