"""Percent Rank parity — independent per-window oracle on synthetic and real data.

No reference library implements this: TA-Lib, pandas-ta(_classic), finta, and ``ta`` all lack
a rolling percent-rank (pandas-ta's ``quantile`` is the unrelated rolling-percentile; there is
no ``percentrank``). So instead of ``importorskip`` on a library we pin against an *independent*
closed-form reimplementation of the spec — "the percent of the prior ``length`` closes strictly
below the current close" — written as a plain per-window Python loop with raw numpy, NOT the
library's own ``percent_rank``/``sliding_window_view`` path. It is a pure count-and-divide with
no smoothing seed and an exact rational result, so parity is bar-for-bar exact (tight rtol/atol)
on both the deterministic walk and committed real market data.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS


def _oracle(close, length: int = 100):
    """Independent percent rank: 100 * (#prior `length` values strictly below current) / length,
    via an explicit per-window loop (no stride tricks). First `length` bars are NaN."""
    c = np.asarray(close, dtype="float64")
    n = c.size
    out = np.full(n, np.nan)
    for i in range(length, n):
        out[i] = 100.0 * int(np.sum(c[i - length : i] < c[i])) / length
    return out


def _p(our, ref, *, rtol=1e-12, atol=1e-12, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_percent_rank_parity_synthetic():
    df = deterministic_frame()
    _p(
        INDICATORS.create("percent_rank", length=100).compute(df)["percent_rank"],
        _oracle(df["close"], 100),
    )


def test_percent_rank_parity_synthetic_short_length():
    df = deterministic_frame()
    _p(
        INDICATORS.create("percent_rank", length=20).compute(df)["percent_rank"],
        _oracle(df["close"], 20),
    )


def test_percent_rank_parity_real():
    df = real_frame()
    _p(
        INDICATORS.create("percent_rank", length=100).compute(df)["percent_rank"],
        _oracle(df["close"], 100),
    )
