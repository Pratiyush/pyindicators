"""RSX — golden + edge cases (Jurik-inspired smoother RSI)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.momentum.rsx import rsx  # noqa: F401  (import fires @INDICATORS.register)


def test_rsx_short_frame_all_nan():
    # Fewer than ``length`` bars cannot seed the cascade -> the whole series is NaN.
    out = INDICATORS.create("rsx", length=14).compute(frame([1.0, 2.0, 3.0]))["rsx"]
    assert out.isna().all()
    assert len(out) == 3


def test_rsx_seeds_one_value_at_length():
    # The reference seeds index ``length-1`` to 0.0; with exactly ``length`` bars that is the
    # single finite value (index 0..length-2 are warm-up NaN, no later bar to compute).
    out = INDICATORS.create("rsx", length=14).compute(frame(np.arange(1.0, 15.0)))["rsx"]
    assert out.notna().sum() == 1
    assert out.iloc[13] == 0.0


def test_rsx_bounded_0_100_on_random_walk():
    out = INDICATORS.create("rsx", length=14).compute(deterministic_frame(400))["rsx"]
    v = out.dropna().to_numpy()
    assert v.size > 100
    assert (v >= 0.0).all() and (v <= 100.0).all()
    assert v.std() > 0  # a real walk must actually vary, not sit pinned at 50


def test_rsx_flat_series_is_neutral():
    # A flat close has zero smoothed magnitude (v20 ~ 0) -> the guard pins output to 50,
    # apart from the 0.0 seed at ``length-1``. So the only finite values are {0, 50}.
    out = INDICATORS.create("rsx", length=14).compute(frame([5.0] * 40))["rsx"]
    assert set(np.unique(out.dropna().to_numpy())) <= {0.0, 50.0}
    assert (out.dropna().to_numpy()[1:] == 50.0).all()  # everything after the seed is neutral


def test_rsx_monotone_up_saturates_high():
    # A pure uptrend drives v14/v20 toward +1 -> output clamps to the 100 ceiling.
    out = INDICATORS.create("rsx", length=14).compute(frame(np.arange(1.0, 120.0)))["rsx"]
    np.testing.assert_allclose(out.dropna().to_numpy()[-5:], 100.0)
