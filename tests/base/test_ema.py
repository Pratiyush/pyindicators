"""EMA — golden + edge cases (incl. both seeding conventions)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.base import ema


def test_constant_series():
    out = INDICATORS.create("ema", length=4).compute(frame([3.0] * 10))
    assert out["ema"].iloc[:3].isna().all()
    np.testing.assert_allclose(out["ema"].iloc[3:], 3.0)


def test_talib_seed_is_sma_of_first_n():
    c = np.arange(1, 11.0)
    out = INDICATORS.create("ema", length=4).compute(frame(c))
    assert out["ema"].iloc[3] == np.mean(c[:4])  # SMA seed at index length-1


def test_pandas_mode_seeds_first_value():
    c = np.arange(1, 11.0)
    s = ema(frame(c)["close"], 4, talib_compatible=False)
    # pandas ewm(adjust=False) recurses from the first value; valid at index length-1
    assert not np.isnan(s.iloc[3])
    assert s.iloc[3] != np.mean(c[:4])  # differs from the SMA-seed convention


def test_short_frame_is_all_nan():
    assert INDICATORS.create("ema", length=20).compute(frame([1.0, 2.0, 3.0]))["ema"].isna().all()
