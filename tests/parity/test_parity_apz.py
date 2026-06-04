"""Adaptive Price Zone (APZ) parity — synthetic and real data.

No reference library implements this exact form: finta's ``APZ`` uses a *DEMA* midline
(``2*EMA - EMA(EMA)``) at the full ``length`` with pandas ``adjust=True`` seeding, whereas
Leibfarth's APZ (the spec here) is a plain *double-smoothed* EMA — ``EMA(EMA(.))`` — at the
short adaptive period ``round(sqrt(length))`` with TA-Lib (SMA-seeded) EMAs. So we assert
against an *independent* closed-form oracle (a from-scratch SMA-seeded double EMA, NOT
``base.ema``) on both the deterministic walk and committed real market data.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS


def _talib_ema(x: np.ndarray, period: int) -> np.ndarray:
    """Independent SMA-seeded EMA (TA-Lib convention): seed = SMA of first ``period`` valid
    values at index ``period-1``, then recurse with alpha = 2/(period+1)."""
    x = np.asarray(x, dtype="float64")
    n = x.size
    out = np.full(n, np.nan)
    valid = np.flatnonzero(~np.isnan(x))
    if valid.size < period:
        return out
    f = int(valid[0])
    alpha = 2.0 / (period + 1.0)
    prev = x[f : f + period].mean()
    out[f + period - 1] = prev
    for i in range(f + period, n):
        prev = alpha * x[i] + (1.0 - alpha) * prev
        out[i] = prev
    return out


def _oracle(df: pd.DataFrame, length: int, mult: float) -> dict[str, np.ndarray]:
    p = max(1, round(math.sqrt(length)))
    mid = _talib_ema(_talib_ema(df["close"].to_numpy(), p), p)
    rng = (df["high"] - df["low"]).to_numpy()
    band = mult * _talib_ema(_talib_ema(rng, p), p)
    return {"apz_middle": mid, "apz_upper": mid + band, "apz_lower": mid - band}


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df: pd.DataFrame, length: int = 21, mult: float = 2.0) -> None:
    out = INDICATORS.create("apz", length=length, mult=mult).compute(df)
    ref = _oracle(df, length, mult)
    for col in ("apz_middle", "apz_upper", "apz_lower"):
        _p(out[col], ref[col])


def test_apz_parity_synthetic():
    _check(deterministic_frame())


def test_apz_parity_synthetic_alt_params():
    _check(deterministic_frame(), length=30, mult=1.5)


def test_apz_parity_real():
    _check(real_frame())
