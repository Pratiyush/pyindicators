"""Derivative Oscillator parity — synthetic and real data.

No reference library ships the Derivative Oscillator (Constance Brown), so we assert
against a closed-form oracle built from pandas-ta's *own* ``rsi`` + ``ema`` + ``sma``
primitives, replicating Brown's cascade ``s = EMA(EMA(RSI,5),3); dosc = s - SMA(s,9)``.
The oracle strips the inner EMA's leading NaN before the outer EMA, exactly as pandas-ta's
internal ``_ema_chain`` (DEMA/TEMA) does. The only residual gap is the EMA seed warm-up,
which converges to machine precision, so we compare a converged tail with rtol.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")


def _oracle(close, rsi_length=14, ema1=5, ema2=3, signal_length=9):
    r = pta.rsi(close, length=rsi_length)
    e1 = pta.ema(r, length=ema1)
    e1 = e1.loc[e1.first_valid_index() :]  # strip inner warm-up NaN (matches _ema_chain)
    smoothed = pta.ema(e1, length=ema2).reindex(close.index)
    signal = pta.sma(smoothed, length=signal_length)
    return smoothed, signal, smoothed - signal


def _p(our, ref, *, rtol=1e-6, atol=1e-9, tail=300, min_overlap=60):
    # tail+rtol: the EMA-of-EMA seed differs by one warm-up bar between libraries but
    # converges exponentially, so only the settled tail is meaningful for parity.
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    our, ref = our[mask][-tail:], ref[mask][-tail:]
    np.testing.assert_allclose(our, ref, rtol=rtol, atol=atol)


def _check(df):
    smoothed, signal, dosc = _oracle(df["close"])
    out = INDICATORS.create("derivative_osc").compute(df)
    _p(out["do_smoothed"], smoothed)
    _p(out["do_signal"], signal)
    _p(out["derivative_osc"], dosc)


def test_dosc_parity_synthetic():
    _check(deterministic_frame())


def test_dosc_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
