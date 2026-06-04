"""RSI Negative Reversal (Cardwell) — golden rule, causality, and edge cases.

No reference library implements Cardwell reversals, so the golden tests pin the explicit rule:
a *confirmed* RSI peak that is a lower high than the prior RSI peak while its bar ``high`` is a
higher high -> 1, emitted on the peak's confirmation bar (peak + ``width``).
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.momentum.rsi import rsi
from pyindicators.momentum.rsi_negative_reversal import (  # noqa: F401  (import fires @register)
    rsi_negative_reversal,
)

# Two-hump fixture (hand-traced below). Choppy 14-bar warm-up seeds RSI ~mid-range, then:
#   peak 1 at bar 15 (RSI 70.45, high 104.5), confirmed at bar 16;
#   peak 2 at bar 21 (RSI 67.38, high 106.5), confirmed at bar 22.
# peak2 is a LOWER RSI high (67.38 < 70.45) while price is a HIGHER high (106.5 > 104.5)
# -> negative reversal, flagged on the confirmation bar 22.
_CLOSE = np.array(
    [100, 100.5, 100, 100.5, 100, 100.5, 100, 100.5, 100, 100.5, 100, 100.5, 100, 100.5,
     102, 104, 103, 101, 100, 102, 104, 106, 105, 103, 102],
    dtype="float64",
)
_HIGH = _CLOSE + 0.5


def _flag(close=_CLOSE, high=_HIGH, length=14, width=1):
    df = frame(close, high=high)
    return INDICATORS.create(
        "rsi_negative_reversal", length=length, width=width
    ).compute(df)["rsi_negative_reversal"]


def test_negative_reversal_fires_once_on_confirmation_bar():
    out = _flag().to_numpy()
    # exactly one negative reversal, on the bar that confirms RSI peak 2 (bar 21 + width 1).
    assert np.flatnonzero(out).tolist() == [22]


def test_golden_peak_relationship_is_lower_rsi_high_higher_price_high():
    # Re-derive the two RSI peaks independently and assert the bearish divergence the flag rests on.
    r = rsi(__import__("pandas").Series(_CLOSE), 14).to_numpy()
    peak1, peak2 = 15, 21
    # both are strict 3-bar local highs in RSI
    assert r[peak1] > r[peak1 - 1] and r[peak1] > r[peak1 + 1]
    assert r[peak2] > r[peak2 - 1] and r[peak2] > r[peak2 + 1]
    assert r[peak2] < r[peak1]  # lower RSI high (momentum weaker)
    assert _HIGH[peak2] > _HIGH[peak1]  # higher price high


def test_no_flag_when_price_high_is_not_higher():
    # Keep the same closes (same RSI peaks) but lower the 2nd peak's bar high below the 1st's:
    # now it is plain bearish agreement (lower RSI high, lower price high) -> NOT a neg reversal.
    high = _HIGH.copy()
    high[21] = _HIGH[15] - 1.0  # 2nd peak high no longer exceeds the 1st
    out = _flag(high=high).to_numpy()
    assert out.sum() == 0.0


def test_first_peak_only_seeds_state_never_flags():
    # A single isolated RSI peak (no prior peak to compare) can never produce a flag.
    close = np.array(
        [100, 100.5, 100, 100.5, 100, 100.5, 100, 100.5, 100, 100.5, 100, 100.5, 100, 100.5,
         103, 106, 104, 102],
        dtype="float64",
    )
    out = _flag(close=close, high=close + 0.5).to_numpy()
    assert out.sum() == 0.0


def test_causal_truncation_does_not_change_earlier_flags():
    # Recompute on the frame truncated right at the flag bar; the flag must be unchanged,
    # proving no dependence on bars after it (strict causality).
    full = _flag().to_numpy()
    cut = 22
    truncated = _flag(close=_CLOSE[: cut + 1], high=_HIGH[: cut + 1]).to_numpy()
    np.testing.assert_array_equal(truncated, full[: cut + 1])
    assert truncated[cut] == 1.0


def test_wider_width_demands_wider_peaks():
    # width=3 requires the peak to dominate 3 neighbours each side; the bar-15/16-style narrow
    # humps in the fixture no longer qualify, so no flag fires.
    out = _flag(width=3).to_numpy()
    assert out.sum() == 0.0


def test_output_is_binary_zero_or_one():
    out = INDICATORS.create("rsi_negative_reversal").compute(deterministic_frame(400))
    v = out["rsi_negative_reversal"].to_numpy()
    assert set(np.unique(v)).issubset({0.0, 1.0})
    assert ((v == 0.0) | (v == 1.0)).all()


def test_fires_on_a_real_random_walk():
    # On 400 bars of the deterministic walk the divergence pattern should occur at least once.
    out = INDICATORS.create("rsi_negative_reversal").compute(deterministic_frame(400))
    assert out["rsi_negative_reversal"].sum() >= 1.0


def test_flat_series_never_flags():
    flat = np.full(60, 100.0)
    out = _flag(close=flat, high=flat).to_numpy()
    assert out.sum() == 0.0


def test_short_frame_all_zero():
    out = _flag(close=np.array([1.0, 2.0, 3.0]), high=np.array([1.5, 2.5, 3.5])).to_numpy()
    assert out.sum() == 0.0


def test_output_contract():
    out = INDICATORS.create("rsi_negative_reversal").compute(deterministic_frame(60))
    assert list(out.columns) == ["rsi_negative_reversal"]
    assert out["rsi_negative_reversal"].dtype == np.float64
    assert len(out) == 60
