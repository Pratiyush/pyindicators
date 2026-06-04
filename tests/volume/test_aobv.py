"""Archer On-Balance Volume — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.volume.aobv import aobv  # noqa: F401  (import fires @register)


def test_aobv_steady_uptrend_obv_and_long_run():
    # Strictly rising close + constant volume V -> OBV adds +V every bar (OBV[0]=V seed),
    # so OBV[i] = (i+1)*V. Both EMAs rise monotonically -> long_run=1, short_run=0.
    n = 60
    v = 1000.0
    c = np.arange(1.0, 1.0 + n)
    out = INDICATORS.create("aobv").compute(frame(c, high=c, low=c, volume=[v] * n))
    np.testing.assert_allclose(out["obv"].to_numpy(), (np.arange(n) + 1) * v)
    tail = slice(40, None)  # well past the slow-EMA + run_length warm-up
    np.testing.assert_array_equal(out["aobv_long_run"].to_numpy()[tail], 1.0)
    np.testing.assert_array_equal(out["aobv_short_run"].to_numpy()[tail], 0.0)


def test_aobv_steady_downtrend_short_run():
    # Strictly falling close -> OBV subtracts V every bar -> both EMAs fall -> short_run=1.
    n = 60
    v = 1000.0
    c = np.arange(1.0 + n, 1.0, -1.0)
    out = INDICATORS.create("aobv").compute(frame(c, high=c, low=c, volume=[v] * n))
    tail = slice(40, None)
    np.testing.assert_array_equal(out["aobv_short_run"].to_numpy()[tail], 1.0)
    np.testing.assert_array_equal(out["aobv_long_run"].to_numpy()[tail], 0.0)


def test_aobv_min_max_bracket_obv():
    # By construction the rolling min/max envelopes must bracket OBV everywhere they exist.
    out = INDICATORS.create("aobv").compute(deterministic_frame(200))
    m = out[["obv", "obv_min", "obv_max"]].dropna()
    assert (m["obv_min"] <= m["obv"] + 1e-9).all()
    assert (m["obv"] <= m["obv_max"] + 1e-9).all()
    # default lookbacks are 2, so min/max warm up after exactly one bar
    assert out["obv_min"].isna().sum() == 1
    assert out["obv_max"].isna().sum() == 1


def test_aobv_outputs_match_spec_and_length():
    df = deterministic_frame(120)
    out = INDICATORS.create("aobv").compute(df)
    assert list(out.columns) == [
        "obv",
        "obv_min",
        "obv_max",
        "obv_fast",
        "obv_slow",
        "aobv_long_run",
        "aobv_short_run",
    ]
    assert len(out) == len(df)
    assert all(str(dt) == "float64" for dt in out.dtypes)
    # run flags are strictly 0/1
    for col in ("aobv_long_run", "aobv_short_run"):
        assert set(np.unique(out[col].to_numpy())) <= {0.0, 1.0}


def test_aobv_short_frame_slow_ema_all_nan_but_obv_defined():
    # 8 bars < slow(12) EMA warm-up: obv_slow all NaN, obv always defined, flags default 0.
    out = INDICATORS.create("aobv").compute(deterministic_frame(8))
    assert out["obv_slow"].isna().all()
    assert out["obv"].notna().all()
    assert (out["aobv_long_run"] == 0.0).all()
    assert (out["aobv_short_run"] == 0.0).all()


def test_aobv_fast_slow_autoswapped():
    # Passing fast>slow must swap so obv_fast warms up before obv_slow (pandas-ta behaviour).
    df = deterministic_frame(60)
    swapped = INDICATORS.create("aobv", fast=12, slow=4).compute(df)
    normal = INDICATORS.create("aobv", fast=4, slow=12).compute(df)
    np.testing.assert_allclose(swapped["obv_fast"].to_numpy(), normal["obv_fast"].to_numpy())
    np.testing.assert_allclose(swapped["obv_slow"].to_numpy(), normal["obv_slow"].to_numpy())
