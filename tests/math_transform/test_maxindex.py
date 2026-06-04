"""MAXINDEX — golden / closed-form + edge cases.

MAXINDEX returns the *absolute* index of the trailing-window maximum (TA-Lib convention),
with the first ``length-1`` bars filled with 0. The tie-break is TA-Lib's exact rule: the
carried maximum is overtaken by a newer equal bar (incremental ``>=``), but a full window
rescan keeps the earliest equal bar (``>``).
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.maxindex import maxindex  # noqa: F401 - import fires @register


def test_maxindex_closed_form_small_window():
    # Window of 3 over a hand-checked series. First two bars are the fill (0). Then each value
    # is the absolute index of the max within {i-2, i-1, i}:
    #   i=2 window[5,3,4] -> idx0=5 is max  -> 0
    #   i=3 window[3,4,2] -> idx2=4 is max  -> 2
    #   i=4 window[4,2,6] -> idx4=6 is max  -> 4
    #   i=5 window[2,6,1] -> idx4=6 is max  -> 4
    out = INDICATORS.create("maxindex", length=3).compute(
        frame([5.0, 3.0, 4.0, 2.0, 6.0, 1.0])
    )["maxindex"]
    np.testing.assert_array_equal(out.to_numpy(), [0.0, 0.0, 0.0, 2.0, 4.0, 4.0])


def test_maxindex_monotonic_increasing_is_current_bar():
    # On a strictly increasing series the max is always the newest bar -> index == i.
    closes = np.arange(1.0, 21.0)
    out = INDICATORS.create("maxindex", length=5).compute(frame(closes))["maxindex"]
    assert (out.iloc[:4] == 0.0).all()  # warm-up fill
    np.testing.assert_array_equal(out.iloc[4:].to_numpy(), np.arange(4.0, 20.0))


def test_maxindex_monotonic_decreasing_tracks_window_start():
    # On a strictly decreasing series the max is always the oldest bar in the window,
    # i.e. absolute index i-(length-1).
    closes = np.arange(20.0, 0.0, -1.0)
    out = INDICATORS.create("maxindex", length=4).compute(frame(closes))["maxindex"]
    np.testing.assert_array_equal(out.iloc[3:].to_numpy(), np.arange(0.0, 17.0))


def test_maxindex_constant_window_resolves_to_earliest_bar():
    # A flat window: the running max is overtaken by newer equal bars (>=) until the leader
    # scrolls out, then the rescan keeps the *earliest* bar. Net effect on a wholly flat
    # series is the oldest index in each window, i.e. i-(length-1).
    out = INDICATORS.create("maxindex", length=4).compute(frame([7.0] * 10))["maxindex"]
    assert (out.iloc[:3] == 0.0).all()
    np.testing.assert_array_equal(out.iloc[3:].to_numpy(), np.arange(0.0, 7.0))


def test_maxindex_tie_break_matches_talib_rule():
    # Hand-traced tie case from probing TA-Lib: input [1,5,5,5,2,2,2,2], length=3.
    #   i=2 window idx{0,1,2}=[1,5,5]: rescan keeps earliest 5 -> 1
    #   i=3 window idx{1,2,3}=[5,5,5]: prev leader idx1 still in window, newest tie wins -> 3
    #   i=4 window idx{2,3,4}=[5,5,2]: leader idx3 in window -> 3
    #   i=5 window idx{3,4,5}=[5,2,2]: leader idx3 in window -> 3
    #   i=6 window idx{4,5,6}=[2,2,2]: leader idx3 left -> rescan earliest -> 4
    #   i=7 window idx{5,6,7}=[2,2,2]: leader idx4 left -> rescan earliest -> 5
    out = INDICATORS.create("maxindex", length=3).compute(
        frame([1.0, 5.0, 5.0, 5.0, 2.0, 2.0, 2.0, 2.0])
    )["maxindex"]
    np.testing.assert_array_equal(out.to_numpy(), [0.0, 0.0, 1.0, 3.0, 3.0, 3.0, 4.0, 5.0])


def test_maxindex_length_two_minimal_window():
    # length=2 points at whichever of {i-1, i} is larger. Tie-break depends on whether the
    # carried leader is still in the 2-bar window:
    #   i=1 [3,1]: leader idx0 (3)                 -> 0
    #   i=2 [1,1]: leader idx0 scrolled out -> rescan {1,2}, earliest tie (>)        -> 1
    #   i=3 [1,4]: idx3 (4) is the new high        -> 3
    #   i=4 [4,4]: leader idx3 still in window, newest equal bar takes over (>=)      -> 4
    out = INDICATORS.create("maxindex", length=2).compute(
        frame([3.0, 1.0, 1.0, 4.0, 4.0])
    )["maxindex"]
    np.testing.assert_array_equal(out.to_numpy(), [0.0, 0.0, 1.0, 3.0, 4.0])


def test_maxindex_short_frame_all_fill():
    # Fewer bars than length -> entire output is the fill value 0.
    out = INDICATORS.create("maxindex", length=30).compute(frame([1.0, 2.0, 3.0]))["maxindex"]
    np.testing.assert_array_equal(out.to_numpy(), [0.0, 0.0, 0.0])


def test_maxindex_warmup_and_contract():
    df = deterministic_frame(200)
    length = 30
    out = INDICATORS.create("maxindex", length=length).compute(df)
    assert list(out.columns) == ["maxindex"]
    assert out["maxindex"].dtype == np.float64
    assert len(out) == len(df)
    idx = out["maxindex"].to_numpy()
    # Warm-up region is the fill 0; from length-1 on, the index is a valid window position.
    assert (idx[: length - 1] == 0.0).all()
    pos = np.arange(len(df), dtype="float64")
    tail = idx[length - 1 :]
    pos_tail = pos[length - 1 :]
    # The returned index is always inside the trailing window [i-(length-1), i].
    assert np.all(tail <= pos_tail)
    assert np.all(tail >= pos_tail - (length - 1))
    # And it genuinely points at the window maximum.
    closes = df["close"].to_numpy()
    for i in range(length - 1, len(df)):
        window = closes[i - (length - 1) : i + 1]
        assert closes[int(idx[i])] == window.max()
