"""Parity for the remaining in-progress indicators (trend/momentum/statistics/relative/
structure): sma_slope, ma_spread, supertrend, long_run, short_run, ttm_momentum,
cmb_composite_index, quantile, hurst_exponent, rs_rating, rolling_high, rolling_low,
pct_from_high, pct_from_low, disparity_index.

A library oracle is used where one ships a matching variant (pandas-ta long_run/short_run);
otherwise an independent definitional reimplementation, or a composition check against
already-verified primitives (EMA/SMA/RSI/linreg), or a structural invariant (Supertrend line
vs close; Hurst band). A real-data sweep adds finiteness + causality coverage on AAPL bars.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.base import ema, sma
from pyindicators.momentum.rsi import rsi
from pyindicators.statistics.linreg import linreg

pta = pytest.importorskip("pandas_ta_classic")

LONG = deterministic_frame()
REAL = real_frame()
C = LONG["close"]


def _close(our, ref, *, rtol=1e-7, atol=1e-7, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


# --- trend: moving-average derivatives -----------------------------------------------------

def test_sma_slope_definition():
    ref = C.rolling(50, min_periods=50).mean().diff()
    _close(INDICATORS.create("sma_slope", length=50).compute(LONG)["sma_slope"], ref,
           rtol=1e-9, atol=1e-9, min_overlap=200)


def test_ma_spread_definition():
    ref = C.rolling(50, min_periods=50).mean() - C.rolling(200, min_periods=200).mean()
    _close(INDICATORS.create("ma_spread", fast=50, slow=200).compute(LONG)["ma_spread"], ref,
           rtol=1e-9, atol=1e-9, min_overlap=150)


def test_long_run_parity_pandas_ta():
    fast, slow = ema(C, 8), ema(C, 21)
    ref = pta.long_run(fast, slow, length=2)
    _close(INDICATORS.create("long_run").compute(LONG)["long_run"], ref, min_overlap=200)


def test_short_run_parity_pandas_ta():
    fast, slow = ema(C, 8), ema(C, 21)
    ref = pta.short_run(fast, slow, length=2)
    _close(INDICATORS.create("short_run").compute(LONG)["short_run"], ref, min_overlap=200)


def test_supertrend_structural():
    out = INDICATORS.create("supertrend", length=10, mult=3.0).compute(LONG)
    line, direction = out["supertrend"].to_numpy(), out["supertrend_dir"].to_numpy()
    close = C.to_numpy()
    m = np.isfinite(line) & np.isfinite(direction)
    assert m.sum() >= 200
    assert set(np.unique(direction[m])).issubset({-1.0, 1.0})
    up, dn = m & (direction == 1.0), m & (direction == -1.0)
    assert up.any() and dn.any()
    eps = 1e-9
    assert np.all(line[up] <= close[up] + eps)   # uptrend: line is the lower (support) band
    assert np.all(line[dn] >= close[dn] - eps)   # downtrend: line is the upper (resistance) band


# --- momentum derivatives ------------------------------------------------------------------

def test_ttm_momentum_composition():
    length = 20
    hh = LONG["high"].rolling(length, min_periods=length).max()
    ll = LONG["low"].rolling(length, min_periods=length).min()
    midline = ((hh + ll) / 2.0 + sma(C, length)) / 2.0
    ref = linreg(C - midline, length)
    _close(INDICATORS.create("ttm_momentum", length=length).compute(LONG)["ttm_momentum"], ref,
           rtol=1e-7, atol=1e-7, min_overlap=200)


def test_cmb_composite_index_composition():
    ref = rsi(C, 14).diff(9) + sma(rsi(C, 3), 3)
    _close(INDICATORS.create("cmb_composite_index").compute(LONG)["cmb_composite_index"], ref,
           rtol=1e-9, atol=1e-9, min_overlap=200)


def test_disparity_index_definition():
    m = C.rolling(14, min_periods=14).mean()
    ref = 100.0 * (C - m) / m
    _close(INDICATORS.create("disparity_index", length=14).compute(LONG)["disparity_index"], ref,
           rtol=1e-9, atol=1e-9, min_overlap=200)


# --- statistics / relative -----------------------------------------------------------------

def test_quantile_definition():
    ref = C.rolling(30, min_periods=30).quantile(0.5)
    _close(INDICATORS.create("quantile", length=30, q=0.5).compute(LONG)["quantile"], ref,
           rtol=1e-9, atol=1e-9, min_overlap=200)


def test_hurst_exponent_structural():
    h = INDICATORS.create("hurst_exponent", length=100).compute(LONG)["hurst_exponent"].dropna()
    assert len(h) > 0
    assert h.between(0.2, 0.9).all()  # random walk -> ~0.5 (with R/S small-sample spread)
    flat = pd.DataFrame({c: np.full(150, 50.0) for c in ("open", "high", "low", "close", "volume")})
    assert INDICATORS.create("hurst_exponent", length=100).compute(flat)["hurst_exponent"].isna().all()


def test_rs_rating_definition():
    lbs, ws = (63, 126, 189, 252), (2.0, 1.0, 1.0, 1.0)
    ref = sum(w * (C / C.shift(lb)) for lb, w in zip(lbs, ws, strict=True)) / sum(ws)
    _close(INDICATORS.create("rs_rating").compute(LONG)["rs_rating"], ref,
           rtol=1e-9, atol=1e-9, min_overlap=100)


# --- structure -----------------------------------------------------------------------------

def test_rolling_high_low_definition():
    _close(INDICATORS.create("rolling_high", length=50).compute(LONG)["rolling_high"],
           LONG["high"].rolling(50, min_periods=50).max(), rtol=0, atol=0, min_overlap=200)
    _close(INDICATORS.create("rolling_low", length=50).compute(LONG)["rolling_low"],
           LONG["low"].rolling(50, min_periods=50).min(), rtol=0, atol=0, min_overlap=200)


def test_pct_from_high_low_definition():
    hh = LONG["high"].rolling(50, min_periods=50).max()
    ll = LONG["low"].rolling(50, min_periods=50).min()
    _close(INDICATORS.create("pct_from_high", length=50).compute(LONG)["pct_from_high"],
           100.0 * (C - hh) / hh, rtol=1e-9, atol=1e-9, min_overlap=200)
    _close(INDICATORS.create("pct_from_low", length=50).compute(LONG)["pct_from_low"],
           100.0 * (C - ll) / ll, rtol=1e-9, atol=1e-9, min_overlap=200)


# --- real-data finiteness + causality ------------------------------------------------------

@pytest.mark.parametrize(
    "name",
    ["sma_slope", "ma_spread", "supertrend", "long_run", "short_run", "ttm_momentum",
     "cmb_composite_index", "quantile", "hurst_exponent", "rs_rating", "rolling_high",
     "rolling_low", "pct_from_high", "pct_from_low", "disparity_index"],
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
