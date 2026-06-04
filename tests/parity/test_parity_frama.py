"""FRAMA parity vs finta — synthetic and real data.

finta's ``TA.FRAMA`` is unrunnable on pandas>=3 / numpy>=2: it does ``filt = c.values`` and then
mutates ``filt`` in place, but ``Series.values`` now returns a read-only array, so the call
raises ``ValueError: assignment destination is read-only``. We therefore pin a line-for-line
copy of finta's published recursion (only change: a writable ``copy`` of the close array) as the
oracle, and ``importorskip`` finta so this still gates on finta being installed.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pytest.importorskip("finta")  # gate on the reference lib even though we run its math directly


def _finta_frama_oracle(df, period=16, batch=10):
    """finta.TA.FRAMA, verbatim, but on a writable close copy (finta's only py3/np2 break)."""
    import pandas as pd

    c = df["close"].copy()
    window = batch * 2
    hh = c.rolling(batch).max()
    ll_ = c.rolling(batch).min()
    n1 = (hh - ll_) / batch
    n2 = n1.shift(batch)
    hh2 = c.rolling(window).max()
    ll2 = c.rolling(window).min()
    n3 = (hh2 - ll2) / window
    with np.errstate(divide="ignore", invalid="ignore"):
        dim = (np.log(n1 + n2) - np.log(n3)) / np.log(2)
        alp = np.exp(-4.6 * (dim - 1))
    alp = np.clip(alp, 0.01, 1).values
    filt = np.array(c.values, copy=True)  # finta uses c.values directly (read-only on np2)
    for i, x in enumerate(alp):
        cl = c.values[i]
        if i < window:
            continue
        filt[i] = cl * x + (1 - x) * filt[i - 1]
    return pd.Series(filt, index=df.index)


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_frama_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("frama", length=16, batch=10).compute(df)["frama"], _finta_frama_oracle(df))


def test_frama_parity_real():
    df = real_frame()
    _p(INDICATORS.create("frama", length=16, batch=10).compute(df)["frama"], _finta_frama_oracle(df))
