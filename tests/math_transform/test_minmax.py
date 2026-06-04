"""Rolling MINMAX — golden / closed-form + edge cases.

MINMAX is a pure rolling reducer (the ``MIN``/``MAX`` pair over one trailing window), so its
behaviour is fully closed-form: each bar is the min and max of the trailing ``length`` closes,
with the first ``length-1`` bars NaN. The structural invariant ``min <= close <= max`` and
``min <= max`` is checked alongside the hand-computed values.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.minmax import minmax  # noqa: F401 - import fires @register


def test_minmax_closed_form_small_window():
    # Window of 3 over a hand-checked series: each bar is the min and the max of itself and
    # the two preceding closes; the first two bars are NaN (undersized window).
    out = INDICATORS.create("minmax", length=3).compute(frame([5.0, 3.0, 4.0, 2.0, 6.0, 1.0]))
    assert out["min"].iloc[:2].isna().all()
    assert out["max"].iloc[:2].isna().all()
    np.testing.assert_array_equal(out["min"].iloc[2:].to_numpy(), [3.0, 2.0, 2.0, 1.0])
    np.testing.assert_array_equal(out["max"].iloc[2:].to_numpy(), [5.0, 4.0, 6.0, 6.0])


def test_minmax_constant_series_collapses_to_level():
    # A flat window has min == max == the constant level once the window fills.
    out = INDICATORS.create("minmax", length=4).compute(frame([7.0] * 10))
    assert out["min"].iloc[:3].isna().all()
    assert out["max"].iloc[:3].isna().all()
    np.testing.assert_array_equal(out["min"].iloc[3:].to_numpy(), np.full(7, 7.0))
    np.testing.assert_array_equal(out["max"].iloc[3:].to_numpy(), np.full(7, 7.0))


def test_minmax_monotonic_increasing_brackets_window_ends():
    # On a strictly increasing series the window minimum is the oldest bar (close shifted back
    # by length-1) and the maximum is the current bar (close itself).
    closes = np.arange(1.0, 21.0)
    out = INDICATORS.create("minmax", length=5).compute(frame(closes))
    np.testing.assert_array_equal(out["min"].iloc[4:].to_numpy(), closes[:-4])
    np.testing.assert_array_equal(out["max"].iloc[4:].to_numpy(), closes[4:])


def test_minmax_min_le_max_invariant():
    # min never exceeds max, and both bracket the current close, on real-ish data.
    df = deterministic_frame(200)
    out = INDICATORS.create("minmax", length=30).compute(df)
    mn = out["min"].iloc[29:].to_numpy()
    mx = out["max"].iloc[29:].to_numpy()
    c = df["close"].iloc[29:].to_numpy()
    assert np.all(mn <= mx + 1e-9)
    assert np.all(mn <= c + 1e-9)
    assert np.all(mx >= c - 1e-9)


def test_minmax_short_frame_all_nan():
    out = INDICATORS.create("minmax", length=30).compute(frame([1.0, 2.0, 3.0]))
    assert out["min"].isna().all()
    assert out["max"].isna().all()


def test_minmax_warmup_and_contract():
    df = deterministic_frame(200)
    out = INDICATORS.create("minmax", length=30).compute(df)
    assert list(out.columns) == ["min", "max"]
    assert out["min"].dtype == np.float64
    assert out["max"].dtype == np.float64
    assert len(out) == len(df)
    for col in ("min", "max"):
        assert out[col].iloc[:29].isna().all()
        assert out[col].iloc[29:].notna().all()
