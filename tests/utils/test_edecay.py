"""EDECAY — Exponential Decay golden + edge cases.

Importing the module directly registers EDECAY (utils is not fully wired into the top-level
package yet). Closed-form / structural assertions live here: the explicit ``max(close,
prev*exp(-1/length))`` recurrence, the bar-0 seed, equality-to-close on a rising/constant
series, geometric decay on a one-shot spike, NaN propagation, the short-frame all-NaN
convention (mirrors the reference returning no series), and param validation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.utils.edecay import edecay  # noqa: F401  (import fires @INDICATORS.register)


def _ref(close: np.ndarray, length: int) -> np.ndarray:
    """Plain-Python oracle of the documented recurrence (independent of the impl)."""
    factor = np.exp(-1.0 / length)
    out = np.empty(close.size, dtype="float64")
    out[0] = close[0]
    for i in range(1, close.size):
        out[i] = max(close[i], out[i - 1] * factor)
    return out


def test_edecay_matches_explicit_recurrence():
    close = np.array([5.0, 3.0, 2.0, 10.0, 1.0, 1.0, 0.5, 7.0])
    out = INDICATORS.create("edecay", length=5).compute(frame(close))["edecay"]
    np.testing.assert_allclose(out.to_numpy(), _ref(close, 5), rtol=1e-12, atol=1e-12)


def test_edecay_seed_is_first_close():
    out = INDICATORS.create("edecay", length=5).compute(frame([42.0, 1.0, 1.0, 1.0, 1.0]))
    assert out["edecay"].iloc[0] == 42.0


def test_edecay_rising_series_equals_close():
    # When close never falls faster than exp(-1/length), the max is always close => identity.
    close = np.arange(1.0, 25.0)
    out = INDICATORS.create("edecay", length=5).compute(frame(close))["edecay"]
    np.testing.assert_allclose(out.to_numpy(), close, rtol=1e-12, atol=1e-12)


def test_edecay_constant_series_equals_close():
    # prev*exp(-1/length) < prev == close, so the floor (close) always wins.
    out = INDICATORS.create("edecay", length=5).compute(frame([4.0] * 8))["edecay"]
    np.testing.assert_allclose(out.to_numpy(), 4.0, rtol=1e-12, atol=1e-12)


def test_edecay_spike_then_geometric_fade():
    # After a lone spike with close dropping to 0, the line decays purely geometrically.
    length = 5
    factor = np.exp(-1.0 / length)
    close = np.array([0.0, 100.0, 0.0, 0.0, 0.0, 0.0])
    out = INDICATORS.create("edecay", length=length).compute(frame(close))["edecay"].to_numpy()
    expected_tail = 100.0 * factor ** np.arange(1, 5)  # bars 2..5 after the spike at bar 1
    np.testing.assert_allclose(out[2:], expected_tail, rtol=1e-12, atol=1e-12)


def test_edecay_nan_close_propagates():
    # A NaN close breaks the recurrence and must not leak stale state afterwards.
    close = np.array([5.0, np.nan, 1.0, 1.0, 1.0])
    out = INDICATORS.create("edecay", length=5).compute(frame(close))["edecay"]
    assert np.isnan(out.iloc[1])
    assert np.isnan(out.iloc[2])  # max(1.0, NaN) is NaN -> carries forward


def test_edecay_short_frame_computes_causally():
    # The recursion is causal, so a frame shorter than `length` still computes (no all-NaN bail)
    # and equals the prefix of a longer frame (truncation-invariant). Rising -> identity.
    out = INDICATORS.create("edecay", length=5).compute(frame([1.0, 2.0, 3.0]))["edecay"]
    np.testing.assert_allclose(out.to_numpy(), [1.0, 2.0, 3.0])


def test_edecay_empty_series():
    assert edecay(pd.Series([], dtype="float64")).empty  # n == 0 guard


def test_edecay_length_one_is_close_floored_recurrence():
    # length=1 => factor=exp(-1)~0.3679; still the documented recurrence, never below close.
    close = np.array([10.0, 1.0, 1.0, 8.0, 1.0])
    out = INDICATORS.create("edecay", length=1).compute(frame(close))["edecay"]
    np.testing.assert_allclose(out.to_numpy(), _ref(close, 1), rtol=1e-12, atol=1e-12)


def test_edecay_never_below_close_on_real_walk():
    df = deterministic_frame(300)
    out = INDICATORS.create("edecay", length=5).compute(df)["edecay"].to_numpy()
    c = df["close"].to_numpy()
    # Floor property: edecay >= close everywhere it is finite.
    assert np.all(out[np.isfinite(out)] >= c[np.isfinite(out)] - 1e-9)


def test_edecay_rejects_unknown_param():
    with pytest.raises((TypeError, ValueError)):
        INDICATORS.create("edecay", window=5)


def test_edecay_rejects_nonpositive_length():
    with pytest.raises((TypeError, ValueError)):
        INDICATORS.create("edecay", length=0)
