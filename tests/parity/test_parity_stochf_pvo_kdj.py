"""Fast Stochastic / PVO / KDJ parity (TA-Lib STOCHF; pandas-ta pvo/kdj)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

LONG = deterministic_frame()
H, L, C = LONG["high"], LONG["low"], LONG["close"]
V = LONG["volume"]


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=80, tail=None):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    if tail is not None:
        our, ref = our[-tail:], ref[-tail:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_stochf_parity_talib():
    talib = pytest.importorskip("talib")
    fastk, fastd = talib.STOCHF(
        H.to_numpy(), L.to_numpy(), C.to_numpy(), fastk_period=14, fastd_period=3, fastd_matype=0
    )
    out = INDICATORS.create("stochf", k=14, d=3).compute(LONG)
    _p(out["stochf_k"], fastk)
    _p(out["stochf_d"], fastd)


def test_pvo_parity_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    ref = pta.pvo(V, fast=12, slow=26, signal=9)
    out = INDICATORS.create("pvo").compute(LONG)
    _p(out["pvo"], ref.iloc[:, 0])
    _p(out["pvo_hist"], ref.iloc[:, 1])
    _p(out["pvo_signal"], ref.iloc[:, 2])


def test_kdj_parity_pandas_ta():
    # Our K/D use the canonical SMA-seeded Wilder RMA (the same smoother as RSI/ATR, matching
    # TA-Lib). pandas-ta's rma seeds at a fixed index and, when KDJ's leading NaNs land on that
    # seed, silently restarts the ewm at the first valid bar — so the two differ only during the
    # warm-up and converge on the tail (alpha=1/3 decays fast). Pinned on the tail.
    pta = pytest.importorskip("pandas_ta_classic")
    ref = pta.kdj(H, L, C, length=9, signal=3)
    out = INDICATORS.create("kdj", length=9, signal=3).compute(LONG)
    _p(out["kdj_k"], ref.iloc[:, 0], tail=300, rtol=1e-5)
    _p(out["kdj_d"], ref.iloc[:, 1], tail=300, rtol=1e-5)
    _p(out["kdj_j"], ref.iloc[:, 2], tail=300, rtol=1e-5)
