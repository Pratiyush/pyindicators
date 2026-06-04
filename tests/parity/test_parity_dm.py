"""+DM / -DM / Aroon Oscillator parity (pandas-ta exact for DM; TA-Lib for AROONOSC)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

LONG = deterministic_frame()
H, L = LONG["high"], LONG["low"]


def _p(our, ref, *, rtol=1e-6, atol=1e-8, min_overlap=100):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_plus_dm_parity_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    _p(INDICATORS.create("plus_dm", length=14).compute(LONG)["plus_dm"],
       pta.plus_dm(H, L, length=14))


def test_minus_dm_parity_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    _p(INDICATORS.create("minus_dm", length=14).compute(LONG)["minus_dm"],
       pta.minus_dm(H, L, length=14))


def test_aroon_osc_parity_talib():
    talib = pytest.importorskip("talib")
    _p(INDICATORS.create("aroon_osc", length=25).compute(LONG)["aroon_osc"],
       talib.AROONOSC(H.to_numpy(), L.to_numpy(), timeperiod=25))
