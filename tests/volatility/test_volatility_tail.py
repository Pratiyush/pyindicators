"""Ulcer, HV, Mass Index, CVI, Chandelier, PDIST, ACCBANDS — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_ulcer_rising_market_is_zero():
    # strictly rising close -> no drawdown -> UI 0
    out = INDICATORS.create("ulcer", length=5).compute(frame(np.arange(1, 30.0)))["ulcer"]
    np.testing.assert_allclose(out.dropna(), 0.0, atol=1e-9)


def test_hv_constant_is_zero():
    out = INDICATORS.create("hv", length=5).compute(frame([5.0] * 20))["hv"]
    np.testing.assert_allclose(out.dropna(), 0.0, atol=1e-9)


def test_hv_matches_formula():
    f = deterministic_frame(80)
    log_ret = np.log(f["close"] / f["close"].shift(1))
    expected = log_ret.rolling(20, min_periods=20).std(ddof=1) * np.sqrt(252) * 100.0
    out = INDICATORS.create("hv", length=20).compute(f)["hv"]
    np.testing.assert_allclose(out.dropna().to_numpy(), expected.dropna().to_numpy(), rtol=1e-9)


def test_massi_finite():
    assert np.isfinite(INDICATORS.create("massi").compute(deterministic_frame(120))["massi"].iloc[-1])


def test_cvi_constant_range_is_zero():
    f = frame([10.0] * 40, high=[11.0] * 40, low=[9.0] * 40)  # constant H-L
    out = INDICATORS.create("cvi", length=5, roc_length=5).compute(f)["cvi"]
    np.testing.assert_allclose(out.dropna(), 0.0, atol=1e-9)


def test_chandelier_stops_bracket_extremes():
    f = deterministic_frame(100)
    out = INDICATORS.create("chandelier").compute(f)
    hh = f["high"].rolling(22, min_periods=22).max()
    ll = f["low"].rolling(22, min_periods=22).min()
    last = out.index[-1]
    assert out["chandelier_long"].loc[last] < hh.loc[last]
    assert out["chandelier_short"].loc[last] > ll.loc[last]


def test_accbands_ordered():
    out = INDICATORS.create("accbands").compute(deterministic_frame(100))
    last = out.iloc[-1]
    assert last["accbands_upper"] > last["accbands_mid"] > last["accbands_lower"]
