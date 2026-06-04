"""DSP parity vs pandas-ta-classic ``dsp`` — synthetic and real data.

TA-Lib has no ``DSP`` function, so the oracle is pandas-ta-classic's ``dsp``
(``close - EMA(close, length)``). With the TA-Lib-compatible (SMA-seeded) EMA our output is
bit-exact (max |Δ| ~5e-14 on both frames), and the NaN warm-up positions match exactly.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.cycle.dsp import dsp  # noqa: F401 — import so @INDICATORS.register fires

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=300):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    # NaN convention must match the oracle exactly (warm-up masking).
    assert np.array_equal(np.isnan(our), np.isnan(ref))
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_dsp_parity_synthetic():
    df = deterministic_frame()
    ours = INDICATORS.create("dsp", length=14).compute(df)["dsp"]
    _p(ours, pta.dsp(df["close"], length=14))


def test_dsp_parity_real():
    df = real_frame()
    ours = INDICATORS.create("dsp", length=14).compute(df)["dsp"]
    _p(ours, pta.dsp(df["close"], length=14))


def test_dsp_parity_alt_lengths():
    df = real_frame()
    for length in (5, 30):
        ours = INDICATORS.create("dsp", length=length).compute(df)["dsp"]
        _p(ours, pta.dsp(df["close"], length=length))


def test_dsp_functional_matches_registry():
    df = real_frame()
    fn = dsp(df["close"], 14)
    reg = INDICATORS.create("dsp", length=14).compute(df)["dsp"]
    np.testing.assert_array_equal(fn.to_numpy(), reg.to_numpy())
