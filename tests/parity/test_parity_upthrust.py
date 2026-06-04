"""Upthrust "parity" — STRUCTURAL, not reference-library.

There is no TA-Lib / pandas-ta / finta / ta Wyckoff-Upthrust oracle, so this file pins the
indicator to its documented closed-form rule by re-deriving it independently with NumPy (a
different code path from the indicator) and asserting an exact match on both the deterministic
walk and genuine AAPL daily bars, plus the structural invariants (domain {-100, 0}, bearish-
only, strict causality). These play the role the reference-library comparison plays for
oracle-backed indicators.

It also cross-checks consistency with the sibling ``spring`` indicator: ``upthrust`` must equal
exactly the bearish (-100) leg of ``spring`` on the same data, so the two never disagree.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.spring import spring  # noqa: F401  (import fires @register)
from pyindicators.candles.upthrust import upthrust  # noqa: F401  (import fires @register)

_LEN = 20


def _reference(df: pd.DataFrame, length: int = _LEN) -> np.ndarray:
    """Independent re-derivation of the upthrust rule (the closed-form spec)."""
    high = df["high"].to_numpy(dtype="float64")
    close = df["close"].to_numpy(dtype="float64")
    n = len(close)
    out = np.zeros(n, dtype="float64")
    for i in range(length, n):
        resistance = high[i - length:i].max()  # prior N highs, current bar excluded
        if high[i] > resistance and close[i] < resistance:
            out[i] = -100.0
    return out


def _ours(df: pd.DataFrame, length: int = _LEN) -> np.ndarray:
    return INDICATORS.create("upthrust", length=length).compute(df)["upthrust"].to_numpy()


def _check(df: pd.DataFrame):
    our = _ours(df)
    ref = _reference(df)
    assert our.shape == ref.shape
    np.testing.assert_array_equal(our, ref)
    # Structural invariants: bearish-only domain.
    assert set(np.unique(our)) <= {-100.0, 0.0}


def test_upthrust_matches_closed_form_synthetic():
    _check(deterministic_frame())


def test_upthrust_matches_closed_form_synthetic_alt_length():
    # A second window so the rule is not pinned to a single lookback.
    df = deterministic_frame()
    np.testing.assert_array_equal(_ours(df, length=10), _reference(df, length=10))


def test_upthrust_matches_closed_form_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_upthrust_fires_on_real_data():
    # The real fixture's volatility actually produces upthrusts, so the closed-form rule is
    # exercised across both output states (not just zeros).
    our = _ours(real_frame())
    assert np.any(our == -100.0)
    assert not np.any(our == 100.0)  # bearish-only: never +100


def test_upthrust_equals_spring_bearish_leg_real():
    # Consistency with the sibling indicator: upthrust must equal exactly the -100 (bearish) leg
    # of ``spring`` on identical data, so the two implementations of the rule agree everywhere.
    df = real_frame()
    sp = INDICATORS.create("spring", length=_LEN).compute(df)["spring"].to_numpy()
    expected = np.where(sp == -100.0, -100.0, 0.0)
    np.testing.assert_array_equal(_ours(df), expected)


def test_upthrust_equals_spring_bearish_leg_synthetic():
    df = deterministic_frame()
    sp = INDICATORS.create("spring", length=_LEN).compute(df)["spring"].to_numpy()
    expected = np.where(sp == -100.0, -100.0, 0.0)
    np.testing.assert_array_equal(_ours(df), expected)


def test_upthrust_is_causal_on_real_data():
    # Truncation invariance: bar i depends only on bars <= i, so computing on a prefix gives the
    # same leading values as computing on the full frame (the no-look-ahead guarantee).
    df = real_frame()
    full = _ours(df)
    for k in (_LEN + 5, len(df) // 2, len(df)):
        np.testing.assert_array_equal(full[:k], _ours(df.iloc[:k].copy()))
