"""HT_DCPERIOD parity vs TA-Lib ``HT_DCPERIOD`` — synthetic and real data.

The Hilbert recurrence reproduces TA-Lib bit-exactly once past the 32-bar lookback (max |Δ|
~3e-12 on both frames), and the NaN-before-lookback positions match exactly.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.cycle.ht_dcperiod import ht_dcperiod  # import so @register fires

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=300):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    # NaN convention must match TA-Lib exactly (warm-up masking).
    assert np.array_equal(np.isnan(our), np.isnan(ref))
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_ht_dcperiod_parity_synthetic():
    df = deterministic_frame()
    ours = INDICATORS.create("ht_dcperiod").compute(df)["ht_dcperiod"]
    _p(ours, talib.HT_DCPERIOD(df["close"].to_numpy()))


def test_ht_dcperiod_parity_real():
    df = real_frame()
    ours = INDICATORS.create("ht_dcperiod").compute(df)["ht_dcperiod"]
    _p(ours, talib.HT_DCPERIOD(df["close"].to_numpy()))


def test_ht_dcperiod_functional_matches_registry():
    df = real_frame()
    fn = ht_dcperiod(df["close"])
    reg = INDICATORS.create("ht_dcperiod").compute(df)["ht_dcperiod"]
    np.testing.assert_array_equal(fn.to_numpy(), reg.to_numpy())
