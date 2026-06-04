"""STARC Bands parity — synthetic and real data.

No reference library ships a STARC function, so the oracle is built from the reference lib's
*own* ``sma`` and ``atr`` (default ``mamode='rma'``, the Wilder-smoothed ATR): the canonical
closed form ``SMA(close, ma_length) +/- mult * ATR(atr_length)``. The middle is a plain SMA and
matches exactly; the bands use tail+rtol because the ATR Wilder seed converges rather than
matching from bar 0 (pandas-ta NaNs the first true range, we seed it as H-L).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")

MA, ATRN, MULT = 5, 15, 2.0


def _tail(our, ref, *, rtol, atol, tail=None, min_overlap=60):
    """Compare the last ``tail`` finite values (default: full overlap). Bands restrict to a
    converged tail because ATR's Wilder seed difference decays as ``(1 - 1/atr_length)**k``."""
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    if tail is not None:
        our, ref = our[-tail:], ref[-tail:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _oracle(df):
    middle = pta.sma(df["close"], length=MA)
    a = pta.atr(df["high"], df["low"], df["close"], length=ATRN)  # mamode='rma' (Wilder)
    return middle, middle + MULT * a, middle - MULT * a


def _check(df):
    out = INDICATORS.create("starc", ma_length=MA, atr_length=ATRN, mult=MULT).compute(df)
    mid, up, lo = _oracle(df)
    # Middle == SMA: both are rolling(MA).mean(), so this is exact over the WHOLE series.
    _tail(out["starc_middle"], mid, rtol=1e-9, atol=1e-9)
    # Bands inherit ATR's Wilder-seed convergence (pandas-ta NaNs the first TR + averages 14
    # values for its seed; we use H-L over 15). The recurrence converges, so the last 60 bars
    # agree to ~1e-13 here — compare that converged tail rather than loosening the tolerance.
    _tail(out["starc_upper"], up, rtol=1e-6, atol=1e-6, tail=60)
    _tail(out["starc_lower"], lo, rtol=1e-6, atol=1e-6, tail=60)


def test_starc_parity_synthetic():
    _check(deterministic_frame())


def test_starc_parity_real():
    _check(real_frame())
