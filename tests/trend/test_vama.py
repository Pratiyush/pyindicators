"""VAMA (Volume Adjusted Moving Average) — closed-form goldens + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.vama import vama  # noqa: F401  (import fires @register for self-test)


def test_vama_constant_close_and_volume_is_the_constant():
    # close=C, volume=V constant: volRatio=C, sum(C*C)/sum(C)=C. Warm-up = 2*(period-1).
    df = frame(np.full(20, 50.0), volume=np.full(20, 1000.0))
    out = INDICATORS.create("vama", period=8).compute(df)["vama"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 50.0, atol=1e-9)
    assert out.isna().sum() == 2 * (8 - 1)  # double-rolling warm-up


def test_vama_constant_volume_is_self_weighted_average():
    # Constant volume cancels in volRatio -> volRatio==close, so VAMA = sum(c^2)/sum(c).
    c = np.array([10.0, 11.0, 12.0, 13.0, 14.0, 15.0], dtype="float64")
    df = frame(c, volume=np.full(c.size, 7.0))
    out = INDICATORS.create("vama", period=3).compute(df)["vama"]
    period = 3
    expected = []
    for i in range(c.size):
        if i < 2 * (period - 1):
            expected.append(np.nan)
        else:
            w = c[i - period + 1 : i + 1]
            expected.append((w * w).sum() / w.sum())
    np.testing.assert_allclose(out.to_numpy(), np.array(expected), atol=1e-9, equal_nan=True)


def test_vama_warmup_is_double_rolling():
    out = INDICATORS.create("vama", period=8).compute(deterministic_frame(200))["vama"]
    assert out.iloc[: 2 * (8 - 1)].isna().all()
    assert np.isfinite(out.iloc[2 * (8 - 1)])  # first real value past warm-up is finite
    v = out.dropna().to_numpy()
    assert v.size > 100 and np.isfinite(v).all() and v.std() > 0


def test_vama_short_frame_all_nan():
    # Fewer than 2*(period-1)+1 rows -> no full double window -> all NaN.
    out = INDICATORS.create("vama", period=8).compute(frame([1.0, 2.0, 3.0]))["vama"]
    assert out.isna().all()


def test_vama_zero_volume_all_nan():
    # Zero mean-volume window -> volRatio guarded to NaN -> result NaN (matches finta 0/0).
    n = 20
    df = frame(100.0 + np.arange(n, dtype="float64"), volume=np.zeros(n))
    out = INDICATORS.create("vama", period=8).compute(df)["vama"]
    assert out.isna().all()


def test_vama_output_contract():
    df = deterministic_frame(60)
    res = INDICATORS.create("vama", period=8).compute(df)
    assert list(res.columns) == ["vama"]
    assert len(res) == len(df)
    assert str(res["vama"].dtype) == "float64"
