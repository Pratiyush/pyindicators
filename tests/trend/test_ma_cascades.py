"""DEMA/TEMA/TRIMA/T3/HMA + PPO/APO/TRIX — golden + edge cases.

A constant series passes through any moving average unchanged, and the oscillators (PPO/
APO/TRIX) are zero on a constant series — cheap, exact correctness anchors.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import frame
from pyindicators import INDICATORS

_MAS = ["dema", "tema", "trima", "t3", "hma"]


@pytest.mark.parametrize("name", _MAS)
def test_ma_of_constant_is_constant(name):
    out = INDICATORS.create(name).compute(frame([7.0] * 200))
    tail = out[name].dropna()
    assert len(tail) > 0
    np.testing.assert_allclose(tail, 7.0, atol=1e-9)


def test_trima_odd_and_even_lengths():
    f = frame(np.arange(1, 60.0))
    odd = INDICATORS.create("trima", length=5).compute(f)["trima"]
    even = INDICATORS.create("trima", length=6).compute(f)["trima"]
    assert np.isfinite(odd.iloc[-1]) and np.isfinite(even.iloc[-1])


def test_ppo_apo_trix_zero_on_constant():
    f = frame([7.0] * 200)
    ppo = INDICATORS.create("ppo").compute(f)
    np.testing.assert_allclose(ppo["ppo"].dropna(), 0.0, atol=1e-9)
    np.testing.assert_allclose(ppo["ppo_hist"].dropna(), 0.0, atol=1e-9)
    apo = INDICATORS.create("apo").compute(f)["apo"].dropna()
    np.testing.assert_allclose(apo, 0.0, atol=1e-9)
    trix = INDICATORS.create("trix").compute(f)["trix"].dropna()
    np.testing.assert_allclose(trix, 0.0, atol=1e-9)


def test_short_frame_all_nan():
    f = frame([1.0, 2.0, 3.0])
    for name in _MAS:
        assert INDICATORS.create(name).compute(f)[name].isna().all()
