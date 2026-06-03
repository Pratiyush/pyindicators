"""Parity of base primitives vs reference libraries (TA-Lib primary; pandas-ta for RMA).

These tests `importorskip` the oracle, so the suite still passes (parity skipped) if it
isn't installed. Reference libraries are used ONLY here, never at runtime.
"""

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


def _parity(our, ref, *, rtol=1e-6, atol=1e-8, min_overlap=100):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap, f"too few comparable points ({mask.sum()})"
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_sma_parity():
    our = INDICATORS.create("sma", length=20).compute(LONG)["sma"]
    _parity(our, talib.SMA(C, timeperiod=20))


def test_ema_parity():
    our = INDICATORS.create("ema", length=20).compute(LONG)["ema"]
    _parity(our, talib.EMA(C, timeperiod=20))


def test_wma_parity():
    our = INDICATORS.create("wma", length=20).compute(LONG)["wma"]
    _parity(our, talib.WMA(C, timeperiod=20))


def test_stdev_parity_population():
    our = INDICATORS.create("stdev", length=20).compute(LONG)["stdev"]
    _parity(our, talib.STDDEV(C, timeperiod=20, nbdev=1))


def test_variance_parity_population():
    our = INDICATORS.create("variance", length=20).compute(LONG)["variance"]
    _parity(our, talib.VAR(C, timeperiod=20, nbdev=1))


def test_true_range_parity():
    # TA-Lib TRANGE is undefined at bar 0 (NaN); our first bar = H-L. The finite-overlap
    # mask drops bar 0, so the rest matches exactly.
    our = INDICATORS.create("true_range").compute(LONG)["true_range"]
    _parity(our, talib.TRANGE(H, L, C))


def test_rma_parity_vs_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    our = INDICATORS.create("rma", length=14).compute(LONG)["rma"]
    _parity(our, pta.rma(LONG["close"], length=14))
