"""Volume parity: TA-Lib (OBV/AD/ADOSC/MFI), pandas-ta (CMF)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")

LONG = deterministic_frame()
H = LONG["high"].to_numpy()
L = LONG["low"].to_numpy()
C = LONG["close"].to_numpy()
V = LONG["volume"].to_numpy()


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=100, tail=None):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    if tail is not None:
        our, ref = our[-tail:], ref[-tail:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_obv_parity():
    _p(INDICATORS.create("obv").compute(LONG)["obv"], talib.OBV(C, V), atol=1e-3)


def test_ad_parity():
    _p(INDICATORS.create("ad").compute(LONG)["ad"], talib.AD(H, L, C, V), atol=1e-3)


def test_adosc_parity_tail():
    _p(INDICATORS.create("adosc").compute(LONG)["adosc"], talib.ADOSC(H, L, C, V, 3, 10),
       rtol=1e-3, tail=200)


def test_mfi_parity():
    _p(INDICATORS.create("mfi", length=14).compute(LONG)["mfi"], talib.MFI(H, L, C, V, 14))


def test_cmf_parity_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    ref = pta.cmf(LONG["high"], LONG["low"], LONG["close"], LONG["volume"], length=20)
    _p(INDICATORS.create("cmf", length=20).compute(LONG)["cmf"], ref)
