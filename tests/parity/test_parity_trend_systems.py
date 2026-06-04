"""Trend-systems parity: DI family / DX / ADXR (TA-Lib + pandas-ta), CHOP/VHF/QStick (pandas-ta)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")
pta = pytest.importorskip("pandas_ta_classic")

LONG = deterministic_frame()
H = LONG["high"].to_numpy()
L = LONG["low"].to_numpy()
C = LONG["close"].to_numpy()


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=80, tail=None):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    if tail is not None:
        our, ref = our[-tail:], ref[-tail:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_plus_minus_di_parity_pandas_ta():
    dmi = pta.adx(LONG["high"], LONG["low"], LONG["close"], length=14)
    _p(INDICATORS.create("plus_di").compute(LONG)["plus_di"], dmi.iloc[:, 1])
    _p(INDICATORS.create("minus_di").compute(LONG)["minus_di"], dmi.iloc[:, 2])


def test_dx_parity_talib_tail():
    _p(INDICATORS.create("dx").compute(LONG)["dx"], talib.DX(H, L, C, 14), rtol=1e-3, tail=200)


def test_adxr_parity_talib_tail():
    _p(INDICATORS.create("adxr").compute(LONG)["adxr"], talib.ADXR(H, L, C, 14), rtol=2e-3, tail=150)


def test_chop_parity_pandas_ta():
    ref = pta.chop(LONG["high"], LONG["low"], LONG["close"], length=14)
    _p(INDICATORS.create("chop", length=14).compute(LONG)["chop"], ref)


def test_vhf_parity_pandas_ta():
    _p(INDICATORS.create("vhf", length=28).compute(LONG)["vhf"], pta.vhf(LONG["close"], length=28))


def test_qstick_parity_pandas_ta():
    ref = pta.qstick(LONG["open"], LONG["close"], length=10)
    _p(INDICATORS.create("qstick", length=10).compute(LONG)["qstick"], ref)
