"""Bollinger Bands — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_constant_series_bands_collapse():
    out = INDICATORS.create("bbands", length=5).compute(frame([7.0] * 12))
    np.testing.assert_allclose(out["bb_middle"].iloc[4:], 7.0)
    np.testing.assert_allclose(out["bb_upper"].iloc[4:], 7.0)  # stdev 0
    np.testing.assert_allclose(out["bb_lower"].iloc[4:], 7.0)
    np.testing.assert_allclose(out["bb_bandwidth"].iloc[4:], 0.0)
    assert out["bb_pctb"].iloc[4:].isna().all()  # 0 / 0 guarded


def test_known_values_population_stdev():
    out = INDICATORS.create("bbands", length=5, mult=2.0).compute(frame([1.0, 2.0, 3.0, 4.0, 5.0]))
    sd = np.std([1, 2, 3, 4, 5])  # population
    np.testing.assert_allclose(out["bb_middle"].iloc[4], 3.0)
    np.testing.assert_allclose(out["bb_upper"].iloc[4], 3 + 2 * sd)
    np.testing.assert_allclose(out["bb_lower"].iloc[4], 3 - 2 * sd)
    np.testing.assert_allclose(out["bb_pctb"].iloc[4], (5 - (3 - 2 * sd)) / (4 * sd))
    np.testing.assert_allclose(out["bb_bandwidth"].iloc[4], 100.0 * (4 * sd) / 3)
