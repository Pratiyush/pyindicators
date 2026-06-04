"""Parabolic SAR — golden + edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.psar import psar


def test_psar_reversal_is_binary():
    out = INDICATORS.create("psar").compute(deterministic_frame(200))
    assert set(np.unique(out["psar_reversal"].to_numpy())) <= {0.0, 1.0}


def test_psar_af_within_bounds():
    out = INDICATORS.create("psar", af0=0.02, max_af=0.2).compute(deterministic_frame(200))
    af = out["psar_af"].dropna().to_numpy()
    assert af.min() >= 0.02 - 1e-12 and af.max() <= 0.2 + 1e-12


def test_psar_trails_below_in_uptrend():
    c = np.arange(1.0, 60.0)
    out = INDICATORS.create("psar").compute(frame(c, high=c + 0.5, low=c - 0.5))["psar"]
    assert out.iloc[-1] < c[-1]  # stop trails below price in a sustained up-trend


def test_psar_single_bar_is_nan():
    out = INDICATORS.create("psar").compute(frame([10.0]))["psar"]
    assert out.isna().all()  # no prior bar to project from


def test_psar_empty_frame():
    empty = pd.DataFrame({"high": [], "low": []}, dtype="float64")
    out = psar(empty)  # m == 0 guard
    assert out["psar"].empty and out["psar_af"].empty
