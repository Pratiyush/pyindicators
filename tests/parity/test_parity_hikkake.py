"""Hikkake parity — EXACT integer match vs ``talib.CDLHIKKAKE`` (synthetic + real).

Hikkake is a stateful multi-bar pattern whose confirmation bar emits ``±200`` (the setup's
``±100`` plus another ``±100``), so the real fixture exercises the full
``{-200, -100, 0, 100, 200}`` value set, not just ``±100``.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.hikkake import hikkake  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("hikkake").compute(df)["hikkake"].to_numpy()
    ref = talib.CDLHIKKAKE(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_hikkake_parity_synthetic():
    _check(deterministic_frame())


def test_hikkake_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLHIKKAKE(*_ohlc(df)).astype("float64")
    assert np.any(np.abs(ref) == 200)  # the real fixture reaches the ±200 confirmation score
    _check(df)
