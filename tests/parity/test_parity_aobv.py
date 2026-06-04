"""Archer On-Balance Volume parity vs pandas-ta — synthetic and real data.

pandas-ta columns (defaults fast=4, slow=12, lookbacks=2, run_length=2, mamode="ema"):
    OBV, OBV_min_2, OBV_max_2, OBVe_4, OBVe_12, AOBV_LR_2, AOBV_SR_2
mapped positionally to our outputs:
    obv, obv_min, obv_max, obv_fast, obv_slow, aobv_long_run, aobv_short_run

OBV and the min/max envelopes match exactly. The EMA columns are tail-compared with rtol:
both libraries SMA-seed the EMA, so they converge but the very first seeded bars can differ
by float rounding. The long/short run flags are derived from the EMAs, so they are also
tail-compared (they agree exactly once the EMAs have warmed up).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df):
    ref = pta.aobv(df["close"], df["volume"])  # defaults: 4/12/2/2 + run_length 2
    out = INDICATORS.create("aobv").compute(df)

    # Exact: OBV and the rolling min/max envelopes are pure cumsum / rolling reductions.
    _p(out["obv"], ref["OBV"], rtol=0, atol=0)
    _p(out["obv_min"], ref["OBV_min_2"], rtol=0, atol=0)
    _p(out["obv_max"], ref["OBV_max_2"], rtol=0, atol=0)

    # EMA of OBV: SMA-seeded both sides -> tail-compare for seed convergence.
    _p(out["obv_fast"], ref["OBVe_4"])
    _p(out["obv_slow"], ref["OBVe_12"])

    # Run flags are exact 0/1; tail-compare to skip the EMA warm-up boundary.
    _p(out["aobv_long_run"], ref["AOBV_LR_2"], rtol=0, atol=0, min_overlap=200)
    _p(out["aobv_short_run"], ref["AOBV_SR_2"], rtol=0, atol=0, min_overlap=200)


def test_aobv_parity_synthetic():
    _check(deterministic_frame())


def test_aobv_parity_real_data():
    _check(real_frame())  # genuine AAPL daily bars
