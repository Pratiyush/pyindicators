"""Adaptive trend indicators: KAMA, Hull MA, Vortex."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from pyindicators import INDICATORS


def _frame(close, *, flat_hl=False):
    close = np.asarray(close, dtype="float64")
    n = len(close)
    ts = pd.date_range("2018-01-01", periods=n, freq="D", tz="UTC")
    high = close if flat_hl else close * 1.01
    low = close if flat_hl else close * 0.99
    return pd.DataFrame({"ts": ts, "open": close, "high": high, "low": low, "close": close,
                         "close_raw": close, "volume": 1e6, "adj_factor": 1.0})


def test_kama_of_constant_is_constant():
    out = INDICATORS.create("kama", period=10).compute(_frame([50.0] * 40, flat_hl=True))
    np.testing.assert_allclose(out["kama"].iloc[10:], 50.0)  # flat ER -> KAMA holds


def test_kama_tracks_uptrend_and_warms_up():
    out = INDICATORS.create("kama", period=10).compute(_frame(np.linspace(100, 200, 60)))
    assert out["kama"].iloc[:10].isna().all()
    assert out["kama"].iloc[-1] > out["kama"].iloc[15]  # rises with price


def test_kama_requires_fast_lt_slow():
    with pytest.raises(ValidationError):
        INDICATORS.create("kama", fast=30, slow=2)


def test_hma_tracks_a_ramp():
    out = INDICATORS.create("hma", period=9).compute(_frame(np.linspace(10, 100, 60)))
    valid = out["hma"].dropna()
    assert (valid.diff().dropna() > 0).all()  # monotone up on a ramp


def test_vortex_positive_and_directional_on_uptrend():
    out = INDICATORS.create("vortex", period=14).compute(_frame(np.linspace(100, 300, 80)))
    last = out.iloc[-1]
    assert last["vi_plus"] >= 0 and last["vi_minus"] >= 0
    assert last["vi_plus"] > last["vi_minus"]  # uptrend -> +VM dominates
