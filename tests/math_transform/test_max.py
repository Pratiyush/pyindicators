"""Rolling MAX — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.max import max  # noqa: A004,F401 - import fires @register


def test_max_closed_form_small_window():
    # Window of 3 over a hand-checked series: each value is the max of itself and the two
    # preceding closes; the first two bars are NaN (undersized window).
    out = INDICATORS.create("max", length=3).compute(frame([5.0, 3.0, 4.0, 2.0, 6.0, 1.0]))["max"]
    assert out.iloc[:2].isna().all()
    np.testing.assert_array_equal(out.iloc[2:].to_numpy(), [5.0, 4.0, 6.0, 6.0])


def test_max_constant_series_is_that_constant():
    # A flat window has max == the constant level once the window fills.
    out = INDICATORS.create("max", length=4).compute(frame([7.0] * 10))["max"]
    assert out.iloc[:3].isna().all()
    np.testing.assert_array_equal(out.iloc[3:].to_numpy(), np.full(7, 7.0))


def test_max_monotonic_increasing_tracks_current_bar():
    # On a strictly increasing series the window maximum is always the newest bar in it,
    # i.e. the current close.
    closes = np.arange(1.0, 21.0)
    out = INDICATORS.create("max", length=5).compute(frame(closes))["max"]
    np.testing.assert_array_equal(out.iloc[4:].to_numpy(), closes[4:])


def test_max_monotonic_decreasing_tracks_window_start():
    # On a strictly decreasing series the window maximum is the oldest bar in it,
    # i.e. close shifted back by length-1.
    closes = np.arange(20.0, 0.0, -1.0)
    out = INDICATORS.create("max", length=5).compute(frame(closes))["max"]
    np.testing.assert_array_equal(out.iloc[4:].to_numpy(), closes[:-4])


def test_max_length_one_is_passthrough():
    closes = [3.0, 1.0, 4.0, 1.0, 5.0]
    out = INDICATORS.create("max", length=1).compute(frame(closes))["max"]
    np.testing.assert_array_equal(out.to_numpy(), closes)


def test_max_short_frame_all_nan():
    out = INDICATORS.create("max", length=30).compute(frame([1.0, 2.0, 3.0]))["max"]
    assert out.isna().all()


def test_max_warmup_and_contract():
    df = deterministic_frame(200)
    out = INDICATORS.create("max", length=30).compute(df)
    assert list(out.columns) == ["max"]
    assert out["max"].dtype == np.float64
    assert len(out) == len(df)
    assert out["max"].iloc[:29].isna().all()
    assert out["max"].iloc[29:].notna().all()
    # The rolling max never falls below the current close (the current bar is in its own window).
    tail = out["max"].iloc[29:].to_numpy()
    assert np.all(tail >= df["close"].iloc[29:].to_numpy() - 1e-9)
