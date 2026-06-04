"""MSW parity vs pandas-ta-classic ``msw`` (native Tulip-Indicators formula).

pandas-ta-classic's ``msw`` passes through to tulipy when present, else uses ``_msw_native``
(the pure-numpy Tulip formula). We reproduce that native path bit-for-bit on both the
deterministic random walk and real AAPL closes; the NaN warm-up (first ``period`` bars)
matches exactly, and the finite overlap agrees to tight tolerance.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.cycle.msw import msw  # import so @register fires

# importorskip resolves the submodule via importlib, so this is the real module object
# (not the re-exported `msw` function the package __init__ would otherwise shadow it with).
pta_msw = pytest.importorskip("pandas_ta_classic.cycles.msw")


def _ref(close, period):
    # Force the native (non-tulipy) path so parity is against the documented numpy formula.
    df = pta_msw.msw(close, period=period, tulipy=False)
    return (
        df[f"MSW_SINE_{period}"].to_numpy(dtype="float64"),
        df[f"MSW_LEAD_{period}"].to_numpy(dtype="float64"),
    )


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=300):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    assert np.array_equal(np.isnan(our), np.isnan(ref))  # warm-up NaN positions identical
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df, period, min_overlap):
    close = df["close"]
    ours = INDICATORS.create("msw", period=period).compute(df)
    ref_sine, ref_lead = _ref(close, period)
    _p(ours["msw_sine"], ref_sine, min_overlap=min_overlap)
    _p(ours["msw_lead"], ref_lead, min_overlap=min_overlap)


def test_msw_parity_synthetic_default():
    _check(deterministic_frame(), period=5, min_overlap=300)


def test_msw_parity_synthetic_longer_period():
    _check(deterministic_frame(), period=12, min_overlap=300)


def test_msw_parity_real():
    df = real_frame()
    # real fixture may be shorter; require a modest finite overlap
    n = len(df)
    _check(df, period=5, min_overlap=min(300, n - 5))


def test_msw_parity_functional_matches_reference():
    close = deterministic_frame()["close"]
    fn = msw(close, period=7)
    ref_sine, ref_lead = _ref(close, 7)
    _p(fn["msw_sine"], ref_sine, min_overlap=300)
    _p(fn["msw_lead"], ref_lead, min_overlap=300)
