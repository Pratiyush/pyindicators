"""MININDEX — golden / closed-form + edge cases (absolute index of the rolling min)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.minindex import minindex  # noqa: F401 - import fires @register


def test_minindex_closed_form_small_window():
    # Window of 3 over a hand-checked series. Each value is the ABSOLUTE index of the lowest
    # close in [i-2, i]; the first two bars are NaN (undersized window).
    #   i=2 win[0:3]=[5,3,4] -> min 3 @1
    #   i=3 win[1:4]=[3,4,2] -> min 2 @3
    #   i=4 win[2:5]=[4,2,6] -> min 2 @3
    #   i=5 win[3:6]=[2,6,1] -> min 1 @5
    out = INDICATORS.create("minindex", length=3).compute(
        frame([5.0, 3.0, 4.0, 2.0, 6.0, 1.0])
    )["minindex"]
    assert out.iloc[:2].isna().all()
    np.testing.assert_array_equal(out.iloc[2:].to_numpy(), [1.0, 3.0, 3.0, 5.0])


def test_minindex_monotonic_increasing_points_at_window_start():
    # Strictly increasing: the minimum is always the OLDEST bar in the window, so the index is
    # i-(length-1).
    closes = np.arange(1.0, 21.0)
    out = INDICATORS.create("minindex", length=5).compute(frame(closes))["minindex"]
    expected = np.arange(20, dtype="float64")[4:] - 4.0
    np.testing.assert_array_equal(out.iloc[4:].to_numpy(), expected)


def test_minindex_monotonic_decreasing_points_at_current_bar():
    # Strictly decreasing: the current bar is always the new low, so the index is i itself.
    closes = np.arange(20.0, 0.0, -1.0)
    out = INDICATORS.create("minindex", length=4).compute(frame(closes))["minindex"]
    expected = np.arange(20, dtype="float64")[3:]
    np.testing.assert_array_equal(out.iloc[3:].to_numpy(), expected)


def test_minindex_constant_series_tracks_earliest_in_window():
    # A flat window has every value tied for the minimum. TA-Lib's scan re-derives the low only
    # when it ages out, then takes the EARLIEST equal value -> the oldest bar in the window.
    out = INDICATORS.create("minindex", length=4).compute(frame([7.0] * 10))["minindex"]
    assert out.iloc[:3].isna().all()
    expected = np.arange(10, dtype="float64")[3:] - 3.0
    np.testing.assert_array_equal(out.iloc[3:].to_numpy(), expected)


def test_minindex_tie_breaking_is_asymmetric():
    # The load-bearing TA-Lib quirk: an equal low arriving INCREMENTALLY (while the running low
    # is still in-window) adopts the LATEST index, whereas np.argmin is always-earliest.
    # closes = [3,1,9,1,9], length 3:
    #   i=2 win[0:3]=[3,1,9]: low rolled in via rescan -> first 1 @1.
    #   i=3 win[1:4]=[1,9,1]: running low @1 is still in-window, so the incremental branch runs;
    #        today's value 1 <= running 1 -> adopt the LATER @3. (np.argmin([1,9,1]) -> @1.)
    #   i=4 win[2:5]=[9,1,9]: low @3 still in-window; 9 <= 1 is false -> stays @3.
    closes = [3.0, 1.0, 9.0, 1.0, 9.0]
    out = INDICATORS.create("minindex", length=3).compute(frame(closes))["minindex"]
    assert out.iloc[:2].isna().all()
    np.testing.assert_array_equal(out.iloc[2:].to_numpy(), [1.0, 3.0, 3.0])
    # np.argmin on the i=3 window would have said @1 (earliest), not @3.
    assert out.iloc[3] != (1 + np.asarray(closes[1:4]).argmin())


def test_minindex_length_two():
    # length 2: index of min(close[i-1], close[i]). A single 2-bar window always re-scans, and
    # a strict-< rescan keeps the EARLIER bar on a tie (window [5,5] at i=2 -> @1, the oldest).
    out = INDICATORS.create("minindex", length=2).compute(
        frame([3.0, 5.0, 5.0, 2.0, 2.0])
    )["minindex"]
    assert np.isnan(out.iloc[0])
    #   i=1 [3,5]->@0 ; i=2 [5,5]->earliest @1 ; i=3 [5,2]->@3 ; i=4 [2,2]->earliest @4
    np.testing.assert_array_equal(out.iloc[1:].to_numpy(), [0.0, 1.0, 3.0, 4.0])


def test_minindex_short_frame_all_nan():
    out = INDICATORS.create("minindex", length=30).compute(frame([1.0, 2.0, 3.0]))["minindex"]
    assert out.isna().all()


def test_minindex_warmup_and_contract():
    df = deterministic_frame(200)
    out = INDICATORS.create("minindex", length=30).compute(df)
    assert list(out.columns) == ["minindex"]
    assert out["minindex"].dtype == np.float64
    assert len(out) == len(df)
    assert out["minindex"].iloc[:29].isna().all()
    assert out["minindex"].iloc[29:].notna().all()
    # The reported index must lie inside the trailing window [i-29, i] and point at the true min.
    idx = out["minindex"].to_numpy()
    closes = df["close"].to_numpy()
    for i in range(29, len(df)):
        j = int(idx[i])
        assert i - 29 <= j <= i
        assert closes[j] == closes[i - 29 : i + 1].min()
