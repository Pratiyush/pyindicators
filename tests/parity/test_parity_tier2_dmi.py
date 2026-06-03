"""Parity for the directional/stateful tier-2: Aroon/ADX/KAMA (TA-Lib), Donchian/Vortex
(pandas-ta). Supertrend is path-dependent (seed-sensitive) and validated structurally."""

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


def _p(our, ref, *, rtol=1e-6, atol=1e-8, min_overlap=100, tail=None):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    if tail is not None:
        our, ref = our[-tail:], ref[-tail:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap, f"too few comparable points ({mask.sum()})"
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_aroon_parity():
    down, up = talib.AROON(H, L, timeperiod=25)
    out = INDICATORS.create("aroon", length=25).compute(LONG)
    _p(out["aroon_down"], down)
    _p(out["aroon_up"], up)
    _p(out["aroon_osc"], talib.AROONOSC(H, L, timeperiod=25))


def test_plus_minus_di_parity():
    out = INDICATORS.create("adx", length=14).compute(LONG)
    _p(out["plus_di"], talib.PLUS_DI(H, L, C, 14))
    _p(out["minus_di"], talib.MINUS_DI(H, L, C, 14))


def test_adx_parity_tail():
    # ADX is doubly Wilder-smoothed; it converges to TA-Lib after the long warm-up.
    out = INDICATORS.create("adx", length=14).compute(LONG)
    _p(out["adx"], talib.ADX(H, L, C, 14), rtol=1e-3, tail=200)


def test_kama_parity_tail():
    # KAMA (TA-Lib fixes fast=2/slow=30; timeperiod is the ER period) converges on the tail.
    our = INDICATORS.create("kama", length=10).compute(LONG)["kama"]
    _p(our, talib.KAMA(C, timeperiod=10), rtol=1e-3, tail=200)


def test_donchian_parity_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    dc = pta.donchian(LONG["high"], LONG["low"], lower_length=20, upper_length=20)
    out = INDICATORS.create("donchian").compute(LONG)
    _p(out["dc_lower"], dc.iloc[:, 0])
    _p(out["dc_middle"], dc.iloc[:, 1])
    _p(out["dc_upper"], dc.iloc[:, 2])


def test_vortex_parity_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    vtx = pta.vortex(LONG["high"], LONG["low"], LONG["close"], length=14)
    out = INDICATORS.create("vortex", length=14).compute(LONG)
    _p(out["vi_plus"], vtx.iloc[:, 0])
    _p(out["vi_minus"], vtx.iloc[:, 1])
