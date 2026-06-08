"""Independent Tulip-Indicators (tulipy) cross-checks for indicators that the other reference
libraries (TA-Lib / pandas-ta / finta / ta) do NOT ship.

For these, our only prior parity was a definitional reimplementation; tulipy is an *independent*
C implementation, so agreement here is genuine third-party correctness evidence (not a tautology
against our own formula). tulipy trims its warm-up, so outputs are left-padded back to length.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import real_frame
from pyindicators import INDICATORS

ti = pytest.importorskip("tulipy")

DF = real_frame()
H, L, C, V = DF["high"], DF["low"], DF["close"], DF["volume"]
HA, LA, CA, VA = H.to_numpy(), L.to_numpy(), C.to_numpy(), V.to_numpy()
OA = DF["open"].to_numpy()


def _p(our, tulip, *, rtol=1e-3, atol=1e-3, tail=200, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.concatenate([np.full(len(DF) - len(tulip), np.nan), np.asarray(tulip, "float64")])
    a, b = our[-tail:], ref[-tail:]
    mask = np.isfinite(a) & np.isfinite(b)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(a[mask], b[mask], rtol=rtol, atol=atol)


def test_wad_tulipy():
    _p(INDICATORS.create("wad").compute(DF)["wad"], ti.wad(HA, LA, CA))


def test_marketfi_tulipy():
    _p(INDICATORS.create("marketfi").compute(DF)["marketfi"], ti.marketfi(HA, LA, VA), rtol=1e-9, atol=1e-12)


def test_cvi_tulipy():
    _p(INDICATORS.create("cvi", length=10, roc_length=10).compute(DF)["cvi"], ti.cvi(HA, LA, 10))


def test_vhf_tulipy():
    _p(INDICATORS.create("vhf", length=28).compute(DF)["vhf"], ti.vhf(CA, 28))


def test_qstick_tulipy():
    _p(INDICATORS.create("qstick", length=10).compute(DF)["qstick"], ti.qstick(OA, CA, 10))


def test_massi_tulipy():
    _p(INDICATORS.create("massi").compute(DF)["massi"], ti.mass(HA, LA, 25))


def test_natr_tulipy():
    _p(INDICATORS.create("natr", length=14).compute(DF)["natr"], ti.natr(HA, LA, CA, 14))


def test_dx_tulipy():
    _p(INDICATORS.create("dx", length=14).compute(DF)["dx"], ti.dx(HA, LA, CA, 14))


def test_adxr_tulipy():
    _p(INDICATORS.create("adxr", length=14).compute(DF)["adxr"], ti.adxr(HA, LA, CA, 14))
