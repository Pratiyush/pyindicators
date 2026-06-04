"""Elder Thermometer / RVI parity vs pandas-ta."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")

LONG = deterministic_frame()
H, L, C = LONG["high"], LONG["low"], LONG["close"]


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=80):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_thermo_parity():
    # pandas-ta columns: [thermo, thermo_ma, thermo_long, thermo_short]
    ref = pta.thermo(H, L, length=20, mamode="ema", long=2, short=0.5)
    out = INDICATORS.create("thermo", length=20, long=2.0, short=0.5).compute(LONG)
    _p(out["thermo"], ref.iloc[:, 0])
    _p(out["thermo_ma"], ref.iloc[:, 1])
    _p(out["thermo_long"], ref.iloc[:, 2])
    _p(out["thermo_short"], ref.iloc[:, 3])


def test_rvi_parity():
    _p(INDICATORS.create("rvi", length=14).compute(LONG)["rvi"], pta.rvi(C, length=14))
