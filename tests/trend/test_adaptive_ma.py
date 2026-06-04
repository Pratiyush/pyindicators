"""VIDYA, McGinley Dynamic, SSF, HWMA — golden + edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.mcgd import mcgd

# MCGD, SSF and HWMA all have unit steady-state gain -> a constant passes through unchanged.
_PASS_THROUGH = ["mcgd", "ssf", "hwma"]


@pytest.mark.parametrize("name", _PASS_THROUGH)
def test_constant_passes_through(name):
    out = INDICATORS.create(name).compute(frame([42.0] * 60))
    np.testing.assert_allclose(out[name].to_numpy(), 42.0, atol=1e-9)


def test_ssf_three_pole_passes_constant():
    out = INDICATORS.create("ssf", length=10, poles=3).compute(frame([5.0] * 40))
    np.testing.assert_allclose(out["ssf"].to_numpy(), 5.0, atol=1e-9)


def test_mcgd_starts_at_first_close():
    out = INDICATORS.create("mcgd").compute(frame([10.0, 11.0, 12.0]))["mcgd"]
    assert out.iloc[0] == 10.0  # seeded with the first close, no warm-up NaN
    assert out.notna().all()


def test_mcgd_empty_series():
    assert mcgd(pd.Series([], dtype="float64")).empty  # n == 0 guard


def test_mcgd_zero_prior_resets_to_close():
    # a zero prior value (degenerate) makes the ratio undefined -> line resets to the close
    out = mcgd(pd.Series([0.0, 5.0, 6.0]))
    assert out.iloc[0] == 0.0
    assert out.iloc[1] == 5.0  # prev == 0 branch


def test_hwma_no_warmup_nan():
    out = INDICATORS.create("hwma").compute(deterministic_frame(50))["hwma"]
    assert out.notna().all()  # recursion runs from bar 0


def test_ssf_short_frame_passes_raw_close():
    # frame shorter than the pole count returns the raw close (filter seed only)
    out = INDICATORS.create("ssf", poles=3).compute(frame([3.0, 4.0]))["ssf"]
    np.testing.assert_allclose(out.to_numpy(), [3.0, 4.0])


def test_vidya_short_frame_all_nan():
    assert INDICATORS.create("vidya", length=14).compute(frame([1.0, 2.0]))["vidya"].isna().all()


def test_vidya_seed_then_finite_and_bounded():
    f = deterministic_frame(200)
    out = INDICATORS.create("vidya", length=14).compute(f)["vidya"]
    vals = out.dropna().to_numpy()
    assert vals.size > 100
    c = f["close"].to_numpy()
    assert vals.min() >= c.min() - 1e-9 and vals.max() <= c.max() + 1e-9


def test_vidya_flat_window_propagates_nan():
    # A flat window makes CMO 0/0 -> NaN, which the recursion carries forward (matches pandas-ta).
    out = INDICATORS.create("vidya", length=10).compute(frame([7.0] * 40))["vidya"]
    assert out.iloc[9] == pytest.approx(7.0)  # SMA seed at length - 1 is finite
    assert out.iloc[10:].isna().all()
