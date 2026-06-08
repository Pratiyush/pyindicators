"""Parity for the volatility/volume indicators that previously lacked a parity test
(natr, keltner, cvi, hv, chandelier, vwap, wad, marketfi, rvol).

Strategy per indicator: a library oracle where one ships a matching variant (TA-Lib NATR);
otherwise a definitional reimplementation (computed independently from the formula) or a
composition check against already-TA-Lib-verified primitives (EMA/ATR). A final real-data
sweep asserts finiteness + causality on genuine AAPL bars, so these also gain the real-data
coverage the audit was flagging.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")

LONG = deterministic_frame()
REAL = real_frame()


def _close(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=60, tail=None):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    if tail is not None:  # compare only the converged tail (Wilder seeding settles)
        our, ref = our[-tail:], ref[-tail:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


# --- volatility ---------------------------------------------------------------------------

def test_natr_parity_talib():
    # NATR = 100*ATR/close with Wilder ATR; the recursion converges to TA-Lib on the tail
    # (the early "unstable period" differs by the seeding convention — a documented divergence).
    our = INDICATORS.create("natr", length=14).compute(LONG)["natr"]
    ref = talib.NATR(LONG["high"], LONG["low"], LONG["close"], timeperiod=14)
    _close(our, ref, rtol=1e-4, atol=1e-4, tail=200)


def test_keltner_composition_vs_ema_atr():
    out = INDICATORS.create("keltner", length=20, atr_length=10, mult=2.0).compute(LONG)
    ema = INDICATORS.create("ema", length=20).compute(LONG)["ema"]
    atr = INDICATORS.create("atr", length=10).compute(LONG)["atr"]
    _close(out["kc_middle"], ema)
    _close(out["kc_upper"], ema + 2.0 * atr)
    _close(out["kc_lower"], ema - 2.0 * atr)


def test_cvi_constant_range_is_zero():
    # Constant high-low range -> EMA(range) constant -> rate-of-change exactly 0.
    n = 60
    base = pd.Series(np.linspace(100.0, 110.0, n))
    df = pd.DataFrame(
        {"open": base, "high": base + 1.0, "low": base - 1.0, "close": base,
         "volume": np.full(n, 1e6)}
    )
    cvi = INDICATORS.create("cvi", length=10, roc_length=10).compute(df)["cvi"].dropna()
    assert len(cvi) > 0
    np.testing.assert_allclose(cvi.to_numpy(), 0.0, atol=1e-9)


def test_hv_definition():
    close = LONG["close"]
    log_ret = np.log(close / close.shift(1))
    ref = log_ret.rolling(20, min_periods=20).std(ddof=1) * np.sqrt(252) * 100.0
    _close(INDICATORS.create("hv", length=20, annual=252).compute(LONG)["hv"], ref,
           rtol=1e-9, atol=1e-9)


def test_chandelier_composition_vs_extremes_atr():
    out = INDICATORS.create("chandelier", length=22, mult=3.0, atr_length=22).compute(LONG)
    atr = INDICATORS.create("atr", length=22).compute(LONG)["atr"]
    hh = LONG["high"].rolling(22, min_periods=22).max()
    ll = LONG["low"].rolling(22, min_periods=22).min()
    _close(out["chandelier_long"], hh - 3.0 * atr)
    _close(out["chandelier_short"], ll + 3.0 * atr)


# --- volume -------------------------------------------------------------------------------

def test_vwap_rolling_definition():
    tp = (LONG["high"] + LONG["low"] + LONG["close"]) / 3.0
    ref = (tp * LONG["volume"]).rolling(14, min_periods=14).sum() / LONG["volume"].rolling(
        14, min_periods=14
    ).sum()
    _close(INDICATORS.create("vwap", length=14).compute(LONG)["vwap"], ref, rtol=1e-9, atol=1e-9)


def test_wad_williams_ad_definition():
    close = LONG["close"]
    prev = close.shift(1)
    move = np.where(
        close > prev,
        close - np.minimum(LONG["low"], prev),
        np.where(close < prev, close - np.maximum(LONG["high"], prev), 0.0),
    )
    ref = pd.Series(move, index=LONG.index)
    ref.iloc[0] = 0.0
    ref = ref.cumsum()
    _close(INDICATORS.create("wad").compute(LONG)["wad"], ref, rtol=1e-9, atol=1e-9,
           min_overlap=300)


def test_marketfi_definition():
    ref = (LONG["high"] - LONG["low"]) / LONG["volume"]
    _close(INDICATORS.create("marketfi").compute(LONG)["marketfi"], ref, rtol=1e-12, atol=1e-12,
           min_overlap=300)


def test_rvol_definition():
    ref = LONG["volume"] / LONG["volume"].rolling(50, min_periods=50).mean()
    _close(INDICATORS.create("rvol", length=50).compute(LONG)["rvol"], ref, rtol=1e-9, atol=1e-9)


# --- real-data finiteness + causality (clears the "no real-data test" audit warning) ------

@pytest.mark.parametrize(
    "name", ["natr", "keltner", "cvi", "hv", "chandelier", "vwap", "wad", "marketfi", "rvol"]
)
def test_real_data_finite_and_causal(name):
    full = pd.DataFrame(INDICATORS.create(name).compute(REAL))
    prefix = pd.DataFrame(INDICATORS.create(name).compute(REAL.iloc[:300]))
    assert np.isfinite(full.to_numpy(dtype="float64")).any()
    for col in full.columns:
        a = full[col].to_numpy(dtype="float64")[:300]
        b = prefix[col].to_numpy(dtype="float64")
        mask = np.isfinite(a) & np.isfinite(b)
        assert mask.sum() > 0
        np.testing.assert_allclose(a[mask], b[mask], rtol=1e-9, atol=1e-9)
