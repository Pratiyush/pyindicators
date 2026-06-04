"""Momentum long-tail parity: TA-Lib (MOM/ROCP/ROCR/ROCR100/CMO/BOP); pandas-ta (AO/Coppock)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")

LONG = deterministic_frame()
OPN = LONG["open"].to_numpy()
H = LONG["high"].to_numpy()
L = LONG["low"].to_numpy()
C = LONG["close"].to_numpy()


def _p(our, ref, *, rtol=1e-6, atol=1e-8, min_overlap=80):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_mom_parity():
    _p(INDICATORS.create("mom", length=10).compute(LONG)["mom"], talib.MOM(C, 10))


def test_rocp_parity():
    _p(INDICATORS.create("rocp", length=10).compute(LONG)["rocp"], talib.ROCP(C, 10))


def test_rocr_parity():
    _p(INDICATORS.create("rocr", length=10).compute(LONG)["rocr"], talib.ROCR(C, 10))


def test_rocr100_parity():
    _p(INDICATORS.create("rocr100", length=10).compute(LONG)["rocr100"], talib.ROCR100(C, 10))


def test_cmo_parity():
    # Chande's original CMO uses simple sums (= pandas-ta). TA-Lib's CMO applies Wilder
    # smoothing (a variant), so parity is pinned against pandas-ta.
    pta = pytest.importorskip("pandas_ta_classic")
    _p(INDICATORS.create("cmo", length=14).compute(LONG)["cmo"], pta.cmo(LONG["close"], length=14))


def test_bop_parity():
    _p(INDICATORS.create("bop").compute(LONG)["bop"], talib.BOP(OPN, H, L, C))


def test_ao_parity_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    _p(INDICATORS.create("ao").compute(LONG)["ao"], pta.ao(LONG["high"], LONG["low"]))


def test_coppock_parity_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    ref = pta.coppock(LONG["close"], length=10, fast=11, slow=14)
    _p(INDICATORS.create("coppock").compute(LONG)["coppock"], ref)
