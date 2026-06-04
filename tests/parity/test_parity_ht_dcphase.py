"""HT_DCPHASE parity vs TA-Lib ``HT_DCPHASE`` — synthetic and real data.

Matches TA-Lib past the 63-bar lookback to ~5e-11 (the residual is float-rounding in the
per-bar arctan/phase accumulation), with identical NaN-before-lookback positions.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.cycle.ht_dcphase import ht_dcphase  # import so @register fires

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=300):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    assert np.array_equal(np.isnan(our), np.isnan(ref))
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_ht_dcphase_parity_synthetic():
    df = deterministic_frame()
    ours = INDICATORS.create("ht_dcphase").compute(df)["ht_dcphase"]
    _p(ours, talib.HT_DCPHASE(df["close"].to_numpy()))


def test_ht_dcphase_parity_real():
    df = real_frame()
    ours = INDICATORS.create("ht_dcphase").compute(df)["ht_dcphase"]
    _p(ours, talib.HT_DCPHASE(df["close"].to_numpy()))


def test_ht_dcphase_functional_matches_registry():
    df = real_frame()
    fn = ht_dcphase(df["close"])
    reg = INDICATORS.create("ht_dcphase").compute(df)["ht_dcphase"]
    np.testing.assert_array_equal(fn.to_numpy(), reg.to_numpy())
