"""Chande Kroll Stop parity vs pandas-ta-classic — synthetic and real data.

Both sides default to TV mode (Wilder/RMA-smoothed ATR, p=10/x=1/q=9). The only divergence
is the ATR *seed*: our ``base.rma`` seeds with the SMA of the first ``p`` true ranges,
whereas pandas-ta's ``rma`` (and its ``true_range``, which NaNs bar 0) seed via an
``ewm``-style transient. That difference decays exponentially — after ~60 valid bars the two
agree to machine precision (verified: max relative diff ~1e-16). So we mask to the finite
overlap, then compare the converged tail.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.trend.cksp import cksp  # noqa: F401  (import fires @register)

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-6, atol=1e-6, tail=200, min_overlap=200):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    our, ref = our[mask], ref[mask]
    assert our.size >= min_overlap
    # Tail only: skip the ATR-seed transient (decayed to machine precision by ~bar 60).
    np.testing.assert_allclose(our[-tail:], ref[-tail:], rtol=rtol, atol=atol)


def _ref(df, p=10, x=1.0, q=9):
    out = pta.cksp(df["high"], df["low"], df["close"], p=p, x=x, q=q, tvmode=True)
    # pandas-ta names columns CKSPl_<p>_<x>_<q> / CKSPs_<p>_<x>_<q>.
    long_col = [c for c in out.columns if c.startswith("CKSPl")][0]
    short_col = [c for c in out.columns if c.startswith("CKSPs")][0]
    return out[long_col], out[short_col]


def test_cksp_parity_synthetic():
    df = deterministic_frame()
    out = INDICATORS.create("cksp", p=10, x=1.0, q=9).compute(df)
    ref_long, ref_short = _ref(df)
    _p(out["cksp_long"], ref_long)
    _p(out["cksp_short"], ref_short)


def test_cksp_parity_real():
    df = real_frame()
    out = INDICATORS.create("cksp", p=10, x=1.0, q=9).compute(df)
    ref_long, ref_short = _ref(df)
    _p(out["cksp_long"], ref_long)
    _p(out["cksp_short"], ref_short)
