"""Price-transform parity: TA-Lib for the algebraic transforms; pandas-ta for Heikin-Ashi."""

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


def _p(our, ref, *, rtol=1e-6, atol=1e-8, min_overlap=100):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_hl2_parity():
    _p(INDICATORS.create("hl2").compute(LONG)["hl2"], talib.MEDPRICE(H, L))


def test_hlc3_parity():
    _p(INDICATORS.create("hlc3").compute(LONG)["hlc3"], talib.TYPPRICE(H, L, C))


def test_ohlc4_parity():
    _p(INDICATORS.create("ohlc4").compute(LONG)["ohlc4"], talib.AVGPRICE(OPN, H, L, C))


def test_wcp_parity():
    _p(INDICATORS.create("wcp").compute(LONG)["wcp"], talib.WCLPRICE(H, L, C))


def test_midpoint_parity():
    _p(INDICATORS.create("midpoint", length=14).compute(LONG)["midpoint"], talib.MIDPOINT(C, 14))


def test_midprice_parity():
    _p(INDICATORS.create("midprice", length=14).compute(LONG)["midprice"], talib.MIDPRICE(H, L, 14))


def test_heikin_ashi_parity_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    ha = pta.ha(LONG["open"], LONG["high"], LONG["low"], LONG["close"])
    out = INDICATORS.create("heikin_ashi").compute(LONG)
    _p(out["ha_open"], ha.iloc[:, 0])
    _p(out["ha_high"], ha.iloc[:, 1])
    _p(out["ha_low"], ha.iloc[:, 2])
    _p(out["ha_close"], ha.iloc[:, 3])
