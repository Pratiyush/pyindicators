"""Tier-2 parity vs TA-Lib (primary) and pandas-ta. Reference libs are test-only."""

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


def test_rsi_parity():
    _p(INDICATORS.create("rsi", length=14).compute(LONG)["rsi"], talib.RSI(C, 14))


def test_willr_parity():
    _p(INDICATORS.create("willr", length=14).compute(LONG)["willr"], talib.WILLR(H, L, C, 14))


def test_cci_parity():
    _p(INDICATORS.create("cci", length=20).compute(LONG)["cci"], talib.CCI(H, L, C, 20))


def test_macd_parity():
    # Our MACD is the standard EMA(fast)-EMA(slow) (Appel / pandas-ta). TA-Lib's MACD
    # restarts the fast EMA at the slow lookback (a documented TA-Lib quirk), so parity is
    # pinned against pandas-ta, which uses the same clean SMA-seeded definition we do.
    pta = pytest.importorskip("pandas_ta_classic")
    md = pta.macd(LONG["close"], fast=12, slow=26, signal=9)
    out = INDICATORS.create("macd").compute(LONG)
    _p(out["macd"], md.iloc[:, 0])
    _p(out["macd_hist"], md.iloc[:, 1])
    _p(out["macd_signal"], md.iloc[:, 2])


def test_bbands_parity():
    u, mid, lo = talib.BBANDS(C, 20, 2, 2, matype=0)
    out = INDICATORS.create("bbands", length=20, mult=2.0).compute(LONG)
    _p(out["bb_upper"], u)
    _p(out["bb_middle"], mid)
    _p(out["bb_lower"], lo)


def test_stoch_parity():
    k, d = talib.STOCH(
        H, L, C, fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0
    )
    out = INDICATORS.create("stoch").compute(LONG)
    _p(out["stoch_k"], k)
    _p(out["stoch_d"], d)


def test_atr_parity_pandas_ta_tail():
    # ATR seeds differ across libraries (TR[0] inclusion); the Wilder recursion converges,
    # so the tail matches pandas-ta closely (cross-checks the TA-Lib convergence below).
    pta = pytest.importorskip("pandas_ta_classic")
    ref = pta.atr(LONG["high"], LONG["low"], LONG["close"], length=14)
    _p(INDICATORS.create("atr", length=14).compute(LONG)["atr"], ref, rtol=1e-3, tail=150)


def test_atr_converges_to_talib_tail():
    # ATR uses TR[0]=H-L (pandas-ta convention); TA-Lib excludes bar 0, so the seeds differ
    # but the Wilder recursion converges — the tail matches TA-Lib closely.
    _p(
        INDICATORS.create("atr", length=14).compute(LONG)["atr"],
        talib.ATR(H, L, C, 14),
        rtol=1e-3,
        tail=150,
    )
