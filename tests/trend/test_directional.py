"""Aroon, Vortex, KAMA, Supertrend, ADX — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


# --- Aroon -------------------------------------------------------------------
def test_aroon_strong_uptrend():
    c = np.arange(1, 40.0)
    out = INDICATORS.create("aroon", length=10).compute(frame(c, high=c, low=c))
    np.testing.assert_allclose(out["aroon_up"].iloc[-1], 100.0)
    np.testing.assert_allclose(out["aroon_down"].iloc[-1], 0.0)
    np.testing.assert_allclose(out["aroon_osc"].iloc[-1], 100.0)


def test_aroon_strong_downtrend():
    c = np.arange(40, 1, -1.0)
    out = INDICATORS.create("aroon", length=10).compute(frame(c, high=c, low=c))
    np.testing.assert_allclose(out["aroon_up"].iloc[-1], 0.0)
    np.testing.assert_allclose(out["aroon_down"].iloc[-1], 100.0)


# --- Vortex ------------------------------------------------------------------
def test_vortex_positive_on_real_data():
    out = INDICATORS.create("vortex", length=14).compute(deterministic_frame(120))
    last = out.iloc[-1]
    assert last["vi_plus"] > 0 and last["vi_minus"] > 0


def test_vortex_flat_is_nan():
    f = frame([5.0] * 40, high=[5.0] * 40, low=[5.0] * 40)
    assert INDICATORS.create("vortex", length=14).compute(f)["vi_plus"].isna().all()


# --- KAMA --------------------------------------------------------------------
def test_kama_constant_stays_flat():
    out = INDICATORS.create("kama", length=10).compute(frame([5.0] * 50))
    np.testing.assert_allclose(out["kama"].dropna(), 5.0)


def test_kama_seed_is_price_at_warmup():
    c = np.arange(1, 30.0)
    out = INDICATORS.create("kama", length=10).compute(frame(c))
    assert out["kama"].iloc[9] == c[9]  # seed at index length-1


def test_kama_short_frame_all_nan():
    assert INDICATORS.create("kama", length=10).compute(frame([1.0] * 5))["kama"].isna().all()


# --- Supertrend --------------------------------------------------------------
def test_supertrend_uptrend_line_below_price():
    c = np.arange(1, 80.0)
    out = INDICATORS.create("supertrend", length=10, mult=3.0).compute(frame(c, high=c + 1, low=c - 1))
    last = out.iloc[-1]
    assert last["supertrend_dir"] == 1.0
    assert last["supertrend"] < c[-1]


def test_supertrend_downtrend_line_above_price():
    c = np.arange(80, 1, -1.0)
    out = INDICATORS.create("supertrend", length=10, mult=3.0).compute(frame(c, high=c + 1, low=c - 1))
    last = out.iloc[-1]
    assert last["supertrend_dir"] == -1.0
    assert last["supertrend"] > c[-1]


def test_supertrend_short_frame_all_nan():
    assert INDICATORS.create("supertrend").compute(frame([1.0, 2.0]))["supertrend"].isna().all()


# --- ADX ---------------------------------------------------------------------
def test_adx_uptrend_plus_di_dominates_and_strong():
    c = np.arange(1, 140.0)
    out = INDICATORS.create("adx", length=14).compute(frame(c, high=c + 0.5, low=c - 0.5))
    last = out.iloc[-1]
    assert last["plus_di"] > last["minus_di"]
    assert last["adx"] > 25.0  # a clean trend is "strong"


def test_adx_outputs_within_bounds():
    out = INDICATORS.create("adx").compute(deterministic_frame(300))
    for col in ("adx", "plus_di", "minus_di"):
        v = out[col].dropna().to_numpy()
        assert (v >= 0).all() and (v <= 100).all()
