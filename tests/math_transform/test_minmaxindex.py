"""MINMAXINDEX — golden / closed-form + edge cases (fused absolute min- and max-index).

MINMAXINDEX returns the *absolute* indices of the trailing-window minimum (``minidx``) and
maximum (``maxidx``), TA-Lib convention, with the first ``length-1`` bars of BOTH outputs filled
with 0. Each tie-break is TA-Lib's exact rule: the carried extreme is overtaken by a newer equal
bar (incremental ``<=`` / ``>=``), but a full window rescan keeps the earliest equal bar
(``<`` / ``>``).
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.minmaxindex import minmaxindex  # noqa: F401 - fires @register


def test_minmaxindex_closed_form_small_window():
    # Window of 3 over a hand-checked series. First two bars are the fill (0). Then each value is
    # the absolute index of the min / max within {i-2, i-1, i}:
    #   i=2 window idx{0,1,2}=[5,3,4] -> min 3 @1 ; max 5 @0
    #   i=3 window idx{1,2,3}=[3,4,2] -> min 2 @3 ; max 4 @2
    #   i=4 window idx{2,3,4}=[4,2,6] -> min 2 @3 ; max 6 @4
    #   i=5 window idx{3,4,5}=[2,6,1] -> min 1 @5 ; max 6 @4
    out = INDICATORS.create("minmaxindex", length=3).compute(
        frame([5.0, 3.0, 4.0, 2.0, 6.0, 1.0])
    )
    np.testing.assert_array_equal(out["minidx"].to_numpy(), [0.0, 0.0, 1.0, 3.0, 3.0, 5.0])
    np.testing.assert_array_equal(out["maxidx"].to_numpy(), [0.0, 0.0, 0.0, 2.0, 4.0, 4.0])


def test_minmaxindex_monotonic_increasing():
    # Strictly increasing: the min is always the OLDEST bar (i-(length-1)); the max is the newest
    # bar (i). Warm-up region is the fill 0.
    closes = np.arange(1.0, 21.0)
    out = INDICATORS.create("minmaxindex", length=5).compute(frame(closes))
    assert (out["minidx"].iloc[:4] == 0.0).all()
    assert (out["maxidx"].iloc[:4] == 0.0).all()
    np.testing.assert_array_equal(out["minidx"].iloc[4:].to_numpy(), np.arange(0.0, 16.0))
    np.testing.assert_array_equal(out["maxidx"].iloc[4:].to_numpy(), np.arange(4.0, 20.0))


def test_minmaxindex_monotonic_decreasing():
    # Strictly decreasing: the min is the newest bar (i); the max is the oldest (i-(length-1)).
    closes = np.arange(20.0, 0.0, -1.0)
    out = INDICATORS.create("minmaxindex", length=4).compute(frame(closes))
    np.testing.assert_array_equal(out["minidx"].iloc[3:].to_numpy(), np.arange(3.0, 20.0))
    np.testing.assert_array_equal(out["maxidx"].iloc[3:].to_numpy(), np.arange(0.0, 17.0))


def test_minmaxindex_constant_series_resolves_to_earliest_in_window():
    # A flat window has every value tied for both extremes. TA-Lib re-derives an extreme only when
    # it ages out, then takes the EARLIEST equal value -> the oldest bar in each window, i.e.
    # i-(length-1). Warm-up is the fill 0.
    out = INDICATORS.create("minmaxindex", length=4).compute(frame([7.0] * 10))
    assert (out["minidx"].iloc[:3] == 0.0).all()
    assert (out["maxidx"].iloc[:3] == 0.0).all()
    np.testing.assert_array_equal(out["minidx"].iloc[3:].to_numpy(), np.arange(0.0, 7.0))
    np.testing.assert_array_equal(out["maxidx"].iloc[3:].to_numpy(), np.arange(0.0, 7.0))


def test_minmaxindex_tie_breaking_is_asymmetric():
    # The load-bearing TA-Lib quirk: an equal extreme arriving INCREMENTALLY (while the running
    # extreme is still in-window) adopts the LATEST index, whereas np.argmin/argmax is always
    # earliest. closes=[3,1,9,1,9], length 3:
    #   i=2 win idx{0,1,2}=[3,1,9]: rescan -> min @1 (earliest 1), max @2 (earliest 9).
    #   i=3 win idx{1,2,3}=[1,9,1]: running min @1 still in-window -> incremental, 1<=1 -> @3;
    #        running max @2 still in-window -> 1>=9 false -> stays @2.
    #   i=4 win idx{2,3,4}=[9,1,9]: min @3 in-window, 9<=1 false -> @3; max @2 in-window,
    #        9>=9 true -> newest wins -> @4.
    closes = [3.0, 1.0, 9.0, 1.0, 9.0]
    out = INDICATORS.create("minmaxindex", length=3).compute(frame(closes))
    np.testing.assert_array_equal(out["minidx"].to_numpy(), [0.0, 0.0, 1.0, 3.0, 3.0])
    np.testing.assert_array_equal(out["maxidx"].to_numpy(), [0.0, 0.0, 2.0, 2.0, 4.0])
    # np.argmin on the i=3 window would have said @1 (earliest), not @3.
    assert out["minidx"].iloc[3] != (1 + np.asarray(closes[1:4]).argmin())


def test_minmaxindex_length_two_minimal_window():
    # length=2 points at whichever of {i-1, i} is the extreme. The tie-break depends on whether the
    # carried leader is still inside the 2-bar window: if so the incremental branch runs and the
    # NEWEST equal bar takes over; only a leader that has scrolled out triggers a strict rescan
    # (earliest). closes=[3,5,5,2,2]:
    #   i=1 [3,5]: min @0 (3), max @1 (5)
    #   i=2 [5,5]: min leader @0 scrolled out -> rescan earliest -> @1; max leader @1 still
    #              in-window, 5>=5 -> newest wins -> @2
    #   i=3 [5,2]: min @3 (2 is the new low); max leader @2 still in-window, 2>=5 false -> @2
    #   i=4 [2,2]: min leader @3 still in-window, 2<=2 -> newest wins -> @4; max leader @2
    #              scrolled out -> rescan earliest -> @3
    out = INDICATORS.create("minmaxindex", length=2).compute(frame([3.0, 5.0, 5.0, 2.0, 2.0]))
    np.testing.assert_array_equal(out["minidx"].to_numpy(), [0.0, 0.0, 1.0, 3.0, 4.0])
    np.testing.assert_array_equal(out["maxidx"].to_numpy(), [0.0, 1.0, 2.0, 2.0, 3.0])


def test_minmaxindex_short_frame_all_fill():
    # Fewer bars than length -> both outputs are entirely the fill value 0.
    out = INDICATORS.create("minmaxindex", length=30).compute(frame([1.0, 2.0, 3.0]))
    np.testing.assert_array_equal(out["minidx"].to_numpy(), [0.0, 0.0, 0.0])
    np.testing.assert_array_equal(out["maxidx"].to_numpy(), [0.0, 0.0, 0.0])


def test_minmaxindex_warmup_and_contract():
    df = deterministic_frame(200)
    length = 30
    out = INDICATORS.create("minmaxindex", length=length).compute(df)
    assert list(out.columns) == ["minidx", "maxidx"]
    assert out["minidx"].dtype == np.float64
    assert out["maxidx"].dtype == np.float64
    assert len(out) == len(df)
    mn = out["minidx"].to_numpy()
    mx = out["maxidx"].to_numpy()
    # Warm-up region is the fill 0 for both.
    assert (mn[: length - 1] == 0.0).all()
    assert (mx[: length - 1] == 0.0).all()
    # From length-1 on, each reported index lies inside the trailing window and points at the true
    # min / max of that window.
    closes = df["close"].to_numpy()
    for i in range(length - 1, len(df)):
        window = closes[i - (length - 1) : i + 1]
        jmin = int(mn[i])
        jmax = int(mx[i])
        assert i - (length - 1) <= jmin <= i
        assert i - (length - 1) <= jmax <= i
        assert closes[jmin] == window.min()
        assert closes[jmax] == window.max()
