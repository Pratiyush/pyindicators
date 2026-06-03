"""Tier-3 parity: ROC/Ultimate Oscillator (TA-Lib); StochRSI/TSI/KST (pandas-ta)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")

LONG = deterministic_frame()
C = LONG["close"].to_numpy()
H = LONG["high"].to_numpy()
L = LONG["low"].to_numpy()


def _p(our, ref, *, rtol=1e-6, atol=1e-8, min_overlap=80, tail=None):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    if tail is not None:
        our, ref = our[-tail:], ref[-tail:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap, f"too few comparable points ({mask.sum()})"
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_roc_parity():
    _p(INDICATORS.create("roc", length=10).compute(LONG)["roc"], talib.ROC(C, 10))


def test_uo_parity():
    _p(INDICATORS.create("uo").compute(LONG)["uo"], talib.ULTOSC(H, L, C, 7, 14, 28))


def test_stochrsi_parity_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    sr = pta.stochrsi(LONG["close"], length=14, rsi_length=14, k=3, d=3)
    out = INDICATORS.create("stochrsi").compute(LONG)
    _p(out["stochrsi_k"], sr.iloc[:, 0])
    _p(out["stochrsi_d"], sr.iloc[:, 1])


def test_tsi_parity_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    t = pta.tsi(LONG["close"], fast=13, slow=25, signal=7)
    _p(INDICATORS.create("tsi").compute(LONG)["tsi"], t.iloc[:, 0])


def test_kst_parity_pandas_ta():
    # Same values; pandas-ta scales KST by an extra 100x. Ours uses ROC-in-percent (Pring /
    # StockCharts convention), so we divide pandas-ta's output by 100 to compare.
    pta = pytest.importorskip("pandas_ta_classic")
    k = pta.kst(LONG["close"])
    _p(INDICATORS.create("kst").compute(LONG)["kst"], k.iloc[:, 0] / 100.0)
