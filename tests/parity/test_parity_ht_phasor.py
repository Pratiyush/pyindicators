"""HT_PHASOR parity vs TA-Lib ``HT_PHASOR`` — synthetic and real data.

TA-Lib ``HT_PHASOR`` returns ``(inphase, quadrature)`` — the raw I1/Q1 phasor components of
the Hilbert pipeline. The recurrence reproduces both bit-exactly once past the 32-bar
lookback (max |Δ| ~2e-12 on both frames), and the NaN-before-lookback positions match.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.cycle.ht_phasor import ht_phasor  # import so @register fires

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=300):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    # NaN convention must match TA-Lib exactly (warm-up masking).
    assert np.array_equal(np.isnan(our), np.isnan(ref))
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df, *, min_overlap=300):
    out = INDICATORS.create("ht_phasor").compute(df)
    ref_in, ref_q = talib.HT_PHASOR(df["close"].to_numpy())
    _p(out["in_phase"], ref_in, min_overlap=min_overlap)
    _p(out["quadrature"], ref_q, min_overlap=min_overlap)


def test_ht_phasor_parity_synthetic():
    _check(deterministic_frame())


def test_ht_phasor_parity_real():
    _check(real_frame())


def test_ht_phasor_functional_matches_registry():
    df = real_frame()
    fn = ht_phasor(df["close"])
    reg = INDICATORS.create("ht_phasor").compute(df)
    np.testing.assert_array_equal(fn["in_phase"].to_numpy(), reg["in_phase"].to_numpy())
    np.testing.assert_array_equal(fn["quadrature"].to_numpy(), reg["quadrature"].to_numpy())
