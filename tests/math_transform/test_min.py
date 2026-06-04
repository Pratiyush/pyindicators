"""Rolling MIN — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.min import min  # noqa: A004,F401 - import fires @register


def test_min_closed_form_small_window():
    # Window of 3 over a hand-checked series: each value is the min of itself and the two
    # preceding closes; the first two bars are NaN (undersized window).
    out = INDICATORS.create("min", length=3).compute(frame([5.0, 3.0, 4.0, 2.0, 6.0, 1.0]))["min"]
    assert out.iloc[:2].isna().all()
    np.testing.assert_array_equal(out.iloc[2:].to_numpy(), [3.0, 2.0, 2.0, 1.0])


def test_min_constant_series_is_that_constant():
    # A flat window has min == the constant level once the window fills.
    out = INDICATORS.create("min", length=4).compute(frame([7.0] * 10))["min"]
    assert out.iloc[:3].isna().all()
    np.testing.assert_array_equal(out.iloc[3:].to_numpy(), np.full(7, 7.0))


def test_min_monotonic_increasing_tracks_window_start():
    # On a strictly increasing series the window minimum is always the oldest bar in it,
    # i.e. close shifted back by length-1.
    closes = np.arange(1.0, 21.0)
    out = INDICATORS.create("min", length=5).compute(frame(closes))["min"]
    np.testing.assert_array_equal(out.iloc[4:].to_numpy(), closes[:-4])


def test_min_length_one_is_passthrough():
    closes = [3.0, 1.0, 4.0, 1.0, 5.0]
    out = INDICATORS.create("min", length=1).compute(frame(closes))["min"]
    np.testing.assert_array_equal(out.to_numpy(), closes)


def test_min_short_frame_all_nan():
    out = INDICATORS.create("min", length=30).compute(frame([1.0, 2.0, 3.0]))["min"]
    assert out.isna().all()


def test_min_warmup_and_contract():
    df = deterministic_frame(200)
    out = INDICATORS.create("min", length=30).compute(df)
    assert list(out.columns) == ["min"]
    assert out["min"].dtype == np.float64
    assert len(out) == len(df)
    assert out["min"].iloc[:29].isna().all()
    assert out["min"].iloc[29:].notna().all()
    # The rolling min never exceeds the current close (the current bar is in its own window).
    tail = out["min"].iloc[29:].to_numpy()
    assert np.all(tail <= df["close"].iloc[29:].to_numpy() + 1e-9)
