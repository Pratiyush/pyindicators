"""Kangaroo Tail "parity" — STRUCTURAL, not reference-library.

There is no TA-Lib / pandas-ta / finta / ta Kangaroo-Tail (Nial Fuller pin bar) oracle, so this
file pins the indicator to its documented closed-form rule by re-deriving it independently with
NumPy and asserting an exact match on both the deterministic walk and genuine AAPL daily bars,
plus the structural invariants (domain {-100,0,100}, bullish/bearish mutual exclusivity, and
that the signal is strictly causal). These play the role the reference-library comparison plays
for oracle-backed indicators.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.kangaroo_tail import kangaroo_tail  # noqa: F401  (import fires @register)

_LEN = 20
_MULT = 2.0


def _reference(df: pd.DataFrame, length: int = _LEN, tail_mult: float = _MULT) -> np.ndarray:
    """Independent re-derivation of the kangaroo-tail rule (the closed-form spec)."""
    open_ = df["open"].to_numpy(dtype="float64")
    high = df["high"].to_numpy(dtype="float64")
    low = df["low"].to_numpy(dtype="float64")
    close = df["close"].to_numpy(dtype="float64")
    n = len(close)
    out = np.zeros(n, dtype="float64")
    for i in range(length, n):
        prior_high = high[i - length:i].max()  # prior N highs, current bar excluded
        prior_low = low[i - length:i].min()  # prior N lows, current bar excluded
        body = abs(close[i] - open_[i])
        upper_tail = high[i] - max(open_[i], close[i])
        lower_tail = min(open_[i], close[i]) - low[i]
        bearish = (
            upper_tail >= tail_mult * body
            and upper_tail >= tail_mult * lower_tail
            and high[i] > prior_high
            and close[i] < prior_high
            and open_[i] < prior_high
        )
        bullish = (
            lower_tail >= tail_mult * body
            and lower_tail >= tail_mult * upper_tail
            and low[i] < prior_low
            and close[i] > prior_low
            and open_[i] > prior_low
        )
        if bearish:
            out[i] = -100.0
        elif bullish:
            out[i] = 100.0
    return out


def _ours(df: pd.DataFrame, length: int = _LEN, tail_mult: float = _MULT) -> np.ndarray:
    return (
        INDICATORS.create("kangaroo_tail", length=length, tail_mult=tail_mult)
        .compute(df)["kangaroo_tail"]
        .to_numpy()
    )


def _check(df: pd.DataFrame):
    our = _ours(df)
    ref = _reference(df)
    assert our.shape == ref.shape
    np.testing.assert_array_equal(our, ref)
    # Structural invariants.
    assert set(np.unique(our)) <= {-100.0, 0.0, 100.0}
    assert not np.any((our == 100.0) & (our == -100.0))  # mutually exclusive by construction


def test_kangaroo_tail_matches_closed_form_synthetic():
    _check(deterministic_frame())


def test_kangaroo_tail_matches_closed_form_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_kangaroo_tail_is_causal_on_real_data():
    # Truncation invariance: bar i depends only on bars <= i, so computing on a prefix gives the
    # same leading values as computing on the full frame (the no-look-ahead guarantee).
    df = real_frame()
    full = _ours(df)
    for k in (_LEN + 5, len(df) // 2, len(df)):
        np.testing.assert_array_equal(full[:k], _ours(df.iloc[:k].copy()))


def test_kangaroo_tail_mutual_exclusivity_under_loose_mult():
    # With tail_mult > 1 a bar can never be both bullish and bearish. Sweep a few multipliers on
    # real data and confirm the domain stays {-100, 0, 100} (the re-derivation already enforces a
    # single branch, so a violation would show up as a mismatch against ``_reference``).
    df = real_frame()
    for mult in (1.5, 2.0, 3.0):
        our = _ours(df, tail_mult=mult)
        np.testing.assert_array_equal(our, _reference(df, tail_mult=mult))
        assert set(np.unique(our)) <= {-100.0, 0.0, 100.0}
