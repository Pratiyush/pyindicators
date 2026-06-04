"""TD Sequential — golden + edge cases (structural, closed-form).

td_seq counts consecutive bars whose close is above / below the close 4 bars earlier,
capped at 13, emitting NaN on bars that are not part of a run. The up and down columns are
complementary (a bar is in at most one run), so every bar has at least one NaN column —
the same by-design property as ``hilo`` / ``qqe``.
"""

from __future__ import annotations

import numpy as np

import pyindicators.momentum.td_seq  # noqa: F401  -- ensure @register fires
from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def _compute(close, **kw):
    return INDICATORS.create("td_seq", **kw).compute(frame(close))


def _capped_ramp(run_bars, cap=13):
    # The count climbs 1,2,3,... but the classic horizon caps it at ``cap``.
    return np.minimum(np.arange(1.0, run_bars + 1.0), float(cap))


def test_monotone_rising_counts_up_only():
    # A strictly rising close is always > the close 4 bars ago: from bar 4 onward the up
    # count climbs (clipped at 13) and the down column is entirely NaN.
    n = 20
    out = _compute(np.arange(1.0, 1.0 + n))
    up = out["td_seq_up"].to_numpy()
    assert np.isnan(up[:4]).all()  # first 4 bars have no 4-bar-ago close
    np.testing.assert_array_equal(up[4:], _capped_ramp(n - 4))
    assert out["td_seq_dn"].isna().all()


def test_monotone_falling_counts_down_only():
    n = 20
    out = _compute(np.arange(1.0 + n, 1.0, -1.0))
    dn = out["td_seq_dn"].to_numpy()
    assert np.isnan(dn[:4]).all()
    np.testing.assert_array_equal(dn[4:], _capped_ramp(n - 4))
    assert out["td_seq_up"].isna().all()


def test_count_is_capped_at_length():
    # A long rising run would count past 13; the classic horizon caps it at 13.
    out = _compute(np.arange(1.0, 60.0))
    up = out["td_seq_up"].dropna().to_numpy()
    assert up.max() == 13.0
    # Configurable cap: a shorter horizon clips lower.
    out5 = _compute(np.arange(1.0, 60.0), length=5)
    assert out5["td_seq_up"].dropna().max() == 5.0


def test_run_resets_after_a_break():
    # Rise for a while, then a single dip below the 4-bar-ago close resets the up run.
    close = list(np.arange(1.0, 11.0)) + [3.0, 12.0, 13.0, 14.0]
    out = _compute(close)
    up = out["td_seq_up"]
    # bar 10 (value 3.0) breaks the up-run (3.0 < close[6]=7.0) -> NaN there...
    assert np.isnan(up.iloc[10])
    # ...and the next up bar restarts the count at 1.
    assert up.iloc[11] == 1.0


def test_flat_vs_four_bars_ago_is_neither_run():
    # close[i] == close[i-4] is strictly neither > nor <, so both columns are NaN there.
    close = [5.0, 6.0, 7.0, 8.0, 5.0]  # bar 4 equals bar 0
    out = _compute(close)
    assert np.isnan(out["td_seq_up"].iloc[4])
    assert np.isnan(out["td_seq_dn"].iloc[4])


def test_columns_are_complementary_each_bar():
    out = INDICATORS.create("td_seq").compute(deterministic_frame(300))
    both = out["td_seq_up"].notna() & out["td_seq_dn"].notna()
    assert not both.any()  # a bar is never in both an up-run and a down-run


def test_short_frame_all_nan():
    out = _compute([1.0, 2.0, 3.0, 4.0])  # only 4 bars -> no diff(4) result
    assert out["td_seq_up"].isna().all()
    assert out["td_seq_dn"].isna().all()


def test_values_within_declared_bounds():
    out = INDICATORS.create("td_seq").compute(deterministic_frame(400))
    for col in ("td_seq_up", "td_seq_dn"):
        v = out[col].to_numpy()
        v = v[np.isfinite(v)]
        assert v.size > 0
        assert v.min() >= 1.0 and v.max() <= 13.0
