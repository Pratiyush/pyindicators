"""ROC, StochRSI, TSI, Ultimate Oscillator — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


# --- ROC ---------------------------------------------------------------------
def test_roc_constant_is_zero():
    out = INDICATORS.create("roc", length=3).compute(frame([5.0] * 8))
    np.testing.assert_allclose(out["roc"].iloc[3:], 0.0)


def test_roc_known_value():
    out = INDICATORS.create("roc", length=1).compute(frame([100.0, 110.0]))
    np.testing.assert_allclose(out["roc"].iloc[1], 10.0)


# --- StochRSI ----------------------------------------------------------------
def test_stochrsi_within_bounds():
    out = INDICATORS.create("stochrsi").compute(deterministic_frame(200))
    v = out["stochrsi_k"].dropna().to_numpy()
    assert ((v >= -1e-9) & (v <= 100 + 1e-9)).all()


def test_stochrsi_flat_is_nan():
    out = INDICATORS.create("stochrsi").compute(frame([5.0] * 60))
    assert out["stochrsi_k"].isna().all()  # flat -> RSI NaN -> StochRSI NaN


# --- TSI ---------------------------------------------------------------------
def test_tsi_monotone_up_is_100():
    out = INDICATORS.create("tsi").compute(frame(np.arange(1, 200.0)))
    np.testing.assert_allclose(out["tsi"].dropna().iloc[-5:], 100.0)


def test_tsi_within_bounds():
    out = INDICATORS.create("tsi").compute(deterministic_frame(200))
    v = out["tsi"].dropna().to_numpy()
    assert ((v >= -100 - 1e-9) & (v <= 100 + 1e-9)).all()


def test_tsi_flat_is_nan():
    out = INDICATORS.create("tsi").compute(frame([5.0] * 100))
    assert out["tsi"].isna().all()


# --- Ultimate Oscillator -----------------------------------------------------
def test_uo_within_bounds():
    out = INDICATORS.create("uo").compute(deterministic_frame(200))
    v = out["uo"].dropna().to_numpy()
    assert ((v >= 0) & (v <= 100)).all()


def test_uo_short_frame_all_nan():
    assert INDICATORS.create("uo").compute(frame([1.0] * 10))["uo"].isna().all()
