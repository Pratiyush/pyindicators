"""HT_SINE parity vs TA-Lib ``HT_SINE`` — synthetic and real data.

TA-Lib returns ``(sine, leadsine)``; both lines match bit-exactly past the 63-bar lookback
(max |Δ| ~4e-12 on both frames), with identical NaN-before-lookback positions.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.cycle.ht_sine import ht_sine  # import so @register fires

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=300):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    # NaN convention must match TA-Lib exactly (warm-up masking).
    assert np.array_equal(np.isnan(our), np.isnan(ref))
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df):
    out = INDICATORS.create("ht_sine").compute(df)
    ref_sine, ref_lead = talib.HT_SINE(df["close"].to_numpy())
    _p(out["sine"], ref_sine)
    _p(out["lead_sine"], ref_lead)


def test_ht_sine_parity_synthetic():
    _check(deterministic_frame())


def test_ht_sine_parity_real():
    _check(real_frame())


def test_ht_sine_functional_matches_registry():
    df = real_frame()
    fn = ht_sine(df["close"])
    reg = INDICATORS.create("ht_sine").compute(df)
    for col in ("sine", "lead_sine"):
        np.testing.assert_array_equal(fn[col].to_numpy(), reg[col].to_numpy())
