"""Spring "parity" — STRUCTURAL, not reference-library.

There is no TA-Lib / pandas-ta Wyckoff-Spring oracle, so this file pins the indicator to its
documented closed-form rule by re-deriving it independently with NumPy and asserting an exact
match on both the deterministic walk and genuine AAPL daily bars, plus the structural
invariants (domain {-100,0,100}, spring/upthrust mutual exclusivity, and that the signal is
strictly causal). These play the role the reference-library comparison plays for oracle-backed
indicators.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.spring import spring  # noqa: F401  (import fires @register)

_LEN = 20


def _reference(df: pd.DataFrame, length: int = _LEN) -> np.ndarray:
    """Independent re-derivation of the spring/upthrust rule (the closed-form spec)."""
    high = df["high"].to_numpy(dtype="float64")
    low = df["low"].to_numpy(dtype="float64")
    close = df["close"].to_numpy(dtype="float64")
    n = len(close)
    out = np.zeros(n, dtype="float64")
    for i in range(length, n):
        support = low[i - length:i].min()  # prior N lows, current bar excluded
        resistance = high[i - length:i].max()  # prior N highs, current bar excluded
        if low[i] < support and close[i] > support:
            out[i] = 100.0
        elif high[i] > resistance and close[i] < resistance:
            out[i] = -100.0
    return out


def _ours(df: pd.DataFrame, length: int = _LEN) -> np.ndarray:
    return INDICATORS.create("spring", length=length).compute(df)["spring"].to_numpy()


def _check(df: pd.DataFrame):
    our = _ours(df)
    ref = _reference(df)
    assert our.shape == ref.shape
    np.testing.assert_array_equal(our, ref)
    # Structural invariants.
    assert set(np.unique(our)) <= {-100.0, 0.0, 100.0}
    assert not np.any((our == 100.0) & (ref == -100.0))  # mutually exclusive by construction


def test_spring_matches_closed_form_synthetic():
    _check(deterministic_frame())


def test_spring_matches_closed_form_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_spring_fires_on_real_data():
    # The real fixture's volatility actually produces both a spring and an upthrust, so the
    # closed-form rule is exercised across all three output states (not just zeros).
    our = _ours(real_frame())
    assert np.any(our == 100.0)
    assert np.any(our == -100.0)


def test_spring_is_causal_on_real_data():
    # Truncation invariance: bar i depends only on bars <= i, so computing on a prefix gives
    # the same leading values as computing on the full frame (the no-look-ahead guarantee).
    df = real_frame()
    full = _ours(df)
    for k in (_LEN + 5, len(df) // 2, len(df)):
        np.testing.assert_array_equal(full[:k], _ours(df.iloc[:k].copy()))
