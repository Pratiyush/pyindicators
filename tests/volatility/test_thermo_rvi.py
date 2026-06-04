"""Elder Thermometer / RVI — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_thermo_flat_is_zero():
    flat = np.full(60, 5.0)
    out = INDICATORS.create("thermo").compute(frame(flat, high=flat, low=flat))
    np.testing.assert_allclose(out["thermo"].dropna().to_numpy(), 0.0, atol=1e-12)
    assert (out["thermo_long"].to_numpy() == 0.0).all()


def test_thermo_signals_are_binary():
    out = INDICATORS.create("thermo").compute(deterministic_frame(120))
    for col in ("thermo_long", "thermo_short"):
        assert set(np.unique(out[col].to_numpy())) <= {0.0, 1.0}


def test_thermo_spikes_on_volatility():
    high = np.array([10.0, 10.0, 10.0, 20.0])  # a big jump on the last bar
    low = np.array([9.0, 9.0, 9.0, 9.0])
    out = INDICATORS.create("thermo", length=2).compute(frame(high, high=high, low=low))
    assert out["thermo"].iloc[-1] > out["thermo"].iloc[-2]


def test_rvi_bounds():
    out = INDICATORS.create("rvi", length=14).compute(deterministic_frame(200))["rvi"]
    v = out.dropna().to_numpy()
    assert v.min() >= -1e-9 and v.max() <= 100.0 + 1e-9


def test_rvi_all_up_days_is_100():
    out = INDICATORS.create("rvi", length=14).compute(frame(np.arange(1.0, 60.0)))["rvi"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 100.0)  # no down-day volatility


def test_rvi_flat_is_nan():
    out = INDICATORS.create("rvi", length=14).compute(frame([5.0] * 60))["rvi"]
    assert out.isna().all()  # zero volatility on both sides -> undefined
