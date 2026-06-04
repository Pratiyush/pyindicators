"""Holt-Winter Channel parity vs pandas_ta_classic — synthetic and real data.

pandas-ta columns (channel_eval=True): [HWM, HWU, HWL, HWW, HWPCT]. The recurrence is
deterministic and seeded at bar 0, so parity is exact (no Wilder/EMA warm-up tail needed);
masking to finite overlap only drops pandas-ta's float-noise zero-width pct on flat stretches.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")

_KW = dict(na=0.2, nb=0.1, nc=0.1, nd=0.1, scalar=1.0)


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=80):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df):
    ref = pta.hwc(df["close"], channel_eval=True, **_KW)
    out = INDICATORS.create("hwc", **_KW).compute(df)
    _p(out["hwc_middle"], ref["HWM"])
    _p(out["hwc_upper"], ref["HWU"])
    _p(out["hwc_lower"], ref["HWL"])
    _p(out["hwc_width"], ref["HWW"])
    _p(out["hwc_pct"], ref["HWPCT"])


def test_hwc_parity_synthetic():
    _check(deterministic_frame())


def test_hwc_parity_real():
    _check(real_frame())


def test_hwc_parity_nondefault_params():
    df = deterministic_frame()
    kw = dict(na=0.3, nb=0.15, nc=0.05, nd=0.2, scalar=2.0)
    ref = pta.hwc(df["close"], channel_eval=True, **kw)
    out = INDICATORS.create("hwc", **kw).compute(df)
    _p(out["hwc_middle"], ref["HWM"])
    _p(out["hwc_upper"], ref["HWU"])
    _p(out["hwc_lower"], ref["HWL"])
    _p(out["hwc_pct"], ref["HWPCT"])
