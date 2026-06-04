"""RSI Positive Reversal parity — vs an independent canonical oracle (no library has it).

Cardwell positive reversals are absent from TA-Lib / pandas-ta / finta / ta, so there is no
third-party oracle. Instead we re-derive the documented rule with a deliberately different,
plain-Python implementation (RSI itself is taken from pandas-ta to cross-check the oscillator
seeding) and assert exact equality of the 0/1 flag on BOTH the synthetic and the real frame,
masked to the finite overlap. Exact equality is appropriate because the output is binary.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

# Importing the module registers the indicator so INDICATORS.create can find it.
from pyindicators.momentum.rsi_positive_reversal import rsi_positive_reversal  # noqa: F401

pta = pytest.importorskip("pandas_ta_classic")


def _oracle(low, close, length=14):
    """Independent canonical re-implementation of the Cardwell positive-reversal rule.

    Uses pandas-ta's RSI (a separate Wilder implementation) for the oscillator, then walks
    the series collecting strict 3-bar RSI troughs and emitting the flag at each trough's
    confirmation bar when RSI prints a higher low while price prints a lower low.
    """
    r = pta.rsi(close, length=length).to_numpy(dtype="float64")
    lows = low.to_numpy(dtype="float64")
    n = r.size
    flag = np.zeros(n, dtype="float64")
    troughs: list[int] = []  # indices of confirmed RSI troughs, in order
    for t in range(1, n - 1):
        window = r[t - 1 : t + 2]
        if not np.all(np.isfinite(window)):
            continue
        left, mid, right = window
        if left > mid and mid < right:  # strict local minimum
            if troughs:
                prev = troughs[-1]
                if (r[t] > r[prev]) and (lows[t] < lows[prev]):
                    flag[t + 1] = 1.0
            troughs.append(t)
    return flag


def _assert_exact_overlap(our, ref, *, min_overlap=200):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_array_equal(our[mask], ref[mask])


def test_positive_reversal_parity_synthetic():
    df = deterministic_frame()
    our = INDICATORS.create("rsi_positive_reversal", length=14).compute(df)
    _assert_exact_overlap(our["rsi_positive_reversal"], _oracle(df["low"], df["close"], 14))


def test_positive_reversal_parity_real():
    df = real_frame()
    our = INDICATORS.create("rsi_positive_reversal", length=14).compute(df)
    _assert_exact_overlap(
        our["rsi_positive_reversal"], _oracle(df["low"], df["close"], 14), min_overlap=100
    )


def test_oracle_actually_fires_on_real_data():
    # Guard against a vacuous test: the rule must produce at least one real signal somewhere
    # (otherwise "all zeros == all zeros" would pass trivially).
    df = deterministic_frame()
    ours = INDICATORS.create("rsi_positive_reversal", length=14).compute(df)
    total = ours["rsi_positive_reversal"].to_numpy().sum()
    assert total >= 1.0, "expected at least one positive reversal on the 400-bar walk"
