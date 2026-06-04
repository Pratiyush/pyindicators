"""MACDFIX parity — exact vs pandas-ta ``macd`` (default branch); shape-only vs TA-Lib.

pandas-ta's default (non-talib) ``macd`` seeds each EMA independently with its own SMA, which
is exactly what our ``base.ema`` composition does -> bit-for-bit equality on the finite
overlap. TA-Lib's ``MACDFIX`` instead seeds the fast EMA from the slow EMA's start; that is a
fixed, non-decaying offset (verified to persist on long smooth series), so we only assert it
agrees in *shape* via a high tail correlation, not in absolute value.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")


def _exact(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _pta_macd(close, signal=9):
    # default talib=False -> clean per-EMA SMA seeding (the exact oracle for our composition)
    df = pta.macd(close, fast=12, slow=26, signal=signal)
    return df.iloc[:, 0], df.iloc[:, 2], df.iloc[:, 1]  # cols: MACD, MACDh, MACDs


@pytest.mark.parametrize("frame_fn", [deterministic_frame, real_frame])
def test_macdfix_parity_pandas_ta_exact(frame_fn):
    df = frame_fn()
    out = INDICATORS.create("macdfix", signal=9).compute(df)
    line, sig, hist = _pta_macd(df["close"], 9)
    _exact(out["macdfix"], line)
    _exact(out["macdfix_signal"], sig)
    _exact(out["macdfix_hist"], hist)


@pytest.mark.parametrize("signal", [5, 9, 13])
def test_macdfix_parity_pandas_ta_signal_periods(signal):
    df = deterministic_frame()
    out = INDICATORS.create("macdfix", signal=signal).compute(df)
    line, sig, hist = _pta_macd(df["close"], signal)
    _exact(out["macdfix"], line)
    _exact(out["macdfix_signal"], sig)
    _exact(out["macdfix_hist"], hist)


def _tail_corr(our, ref, *, k=120, min_overlap=80):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    a, b = our[mask][-k:], ref[mask][-k:]
    return float(np.corrcoef(a, b)[0, 1])


@pytest.mark.parametrize("frame_fn", [deterministic_frame, real_frame])
def test_macdfix_shape_matches_talib(frame_fn):
    talib = pytest.importorskip("talib")
    df = frame_fn()
    out = INDICATORS.create("macdfix", signal=9).compute(df)
    tmacd, tsig, thist = talib.MACDFIX(df["close"].to_numpy(dtype="float64"), signalperiod=9)
    # Shape-only: TA-Lib's fast-EMA seeding gives a fixed absolute offset (~1e-2..2e-1) that
    # never decays, but the curves are otherwise the same shape -> tail correlation ~1.
    assert _tail_corr(out["macdfix"], tmacd) > 0.999
    assert _tail_corr(out["macdfix_signal"], tsig) > 0.999
    assert _tail_corr(out["macdfix_hist"], thist) > 0.999
