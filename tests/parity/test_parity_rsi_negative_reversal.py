"""RSI Negative Reversal parity — independent closed-form oracle on synthetic and real data.

No reference library implements Cardwell positive/negative reversals: TA-Lib, pandas-ta(_classic),
finta, and ``ta`` all lack them. So instead of ``importorskip`` we pin against an *independent*
reimplementation of the published rule, written with raw pandas/numpy (its own Wilder-RSI and a
vectorised peak mask) rather than the library's ``rsi`` / single-pass loop. Because the flag is a
pure comparison of successive confirmed RSI peaks (no smoothing of the flag itself), parity is
exact (atol 0), checked bar-for-bar on both the synthetic walk and real market data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS


def _wilder_rsi(close: pd.Series, length: int) -> np.ndarray:
    """Independent Wilder RSI: SMA-seeded RMA of gains/losses (no library helpers)."""
    delta = close.diff()
    gain = delta.clip(lower=0.0).to_numpy(dtype="float64")
    loss = (-delta).clip(lower=0.0).to_numpy(dtype="float64")
    n = close.size
    ag = np.full(n, np.nan)
    al = np.full(n, np.nan)
    if n > length:
        ag[length] = np.nanmean(gain[1 : length + 1])  # bar 0 gain is NaN (no prior close)
        al[length] = np.nanmean(loss[1 : length + 1])
        for i in range(length + 1, n):
            ag[i] = (ag[i - 1] * (length - 1) + gain[i]) / length
            al[i] = (al[i - 1] * (length - 1) + loss[i]) / length
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = ag / al
        return 100.0 - 100.0 / (1.0 + rs)


def _oracle(df: pd.DataFrame, length: int = 14, width: int = 1) -> np.ndarray:
    """Independent Cardwell negative reversal via a vectorised peak mask + peak-pair scan."""
    r = _wilder_rsi(df["close"], length)
    high = df["high"].to_numpy(dtype="float64")
    n = r.size

    # Strict local-high mask (peak strictly above its `width` neighbours both sides).
    is_peak = np.zeros(n, dtype=bool)
    for t in range(width, n - width):
        win = r[t - width : t + width + 1]
        if np.isnan(win).any():
            continue
        if r[t] > win[:width].max() and r[t] > win[width + 1 :].max():
            is_peak[t] = True

    peaks = np.flatnonzero(is_peak)  # peak bar indices in time order
    flag = np.zeros(n, dtype="float64")
    for k in range(1, peaks.size):
        prev, cur = peaks[k - 1], peaks[k]
        if r[cur] < r[prev] and high[cur] > high[prev]:
            flag[cur + width] = 1.0  # confirmation bar
    return flag


def _p(our, ref, *, atol=0.0, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=0.0, atol=atol)


def test_rsi_negative_reversal_parity_synthetic():
    df = deterministic_frame()
    out = INDICATORS.create("rsi_negative_reversal", length=14, width=1).compute(df)
    _p(out["rsi_negative_reversal"], _oracle(df, 14, 1))


def test_rsi_negative_reversal_parity_real():
    df = real_frame()
    out = INDICATORS.create("rsi_negative_reversal", length=14, width=1).compute(df)
    _p(out["rsi_negative_reversal"], _oracle(df, 14, 1))


def test_rsi_negative_reversal_parity_wider_width():
    df = deterministic_frame()
    out = INDICATORS.create("rsi_negative_reversal", length=14, width=2).compute(df)
    _p(out["rsi_negative_reversal"], _oracle(df, 14, 2))
