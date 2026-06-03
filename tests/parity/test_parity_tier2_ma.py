"""Parity for the MA cascades + PPO/APO/TRIX. TA-Lib where it uses the clean definition,
pandas-ta for HMA/PPO/APO (TA-Lib restarts the fast EMA in PPO/APO)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")

LONG = deterministic_frame()
C = LONG["close"].to_numpy()


def _p(our, ref, *, rtol=1e-6, atol=1e-8, min_overlap=100, tail=None):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    if tail is not None:
        our, ref = our[-tail:], ref[-tail:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap, f"too few comparable points ({mask.sum()})"
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_dema_parity():
    _p(INDICATORS.create("dema", length=20).compute(LONG)["dema"], talib.DEMA(C, 20))


def test_tema_parity():
    _p(INDICATORS.create("tema", length=20).compute(LONG)["tema"], talib.TEMA(C, 20))


def test_trima_parity_even():
    _p(INDICATORS.create("trima", length=20).compute(LONG)["trima"], talib.TRIMA(C, 20))


def test_trima_parity_odd():
    _p(INDICATORS.create("trima", length=21).compute(LONG)["trima"], talib.TRIMA(C, 21))


def test_t3_parity():
    _p(INDICATORS.create("t3", length=5, vfactor=0.7).compute(LONG)["t3"], talib.T3(C, 5, 0.7))


def test_trix_parity_line():
    _p(INDICATORS.create("trix", length=15).compute(LONG)["trix"], talib.TRIX(C, 15))


def test_hma_parity_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    _p(INDICATORS.create("hma", length=16).compute(LONG)["hma"], pta.hma(LONG["close"], length=16))


def test_ppo_parity():
    # EMA-based PPO == TA-Lib PPO with matype=1. (pandas-ta defaults PPO/APO to SMA.)
    _p(INDICATORS.create("ppo").compute(LONG)["ppo"], talib.PPO(C, 12, 26, matype=1))


def test_apo_parity():
    _p(INDICATORS.create("apo").compute(LONG)["apo"], talib.APO(C, 12, 26, matype=1))
