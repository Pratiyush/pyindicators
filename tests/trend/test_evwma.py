"""EVWMA (Elastic Volume Weighted MA) — closed-form goldens + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.evwma import evwma  # noqa: F401  (import fires @register for self-test)


def _golden(close, volume, period):
    """Reference recurrence (the documented finta formula) with NaN warm-up, for goldens."""
    close = np.asarray(close, dtype="float64")
    volume = np.asarray(volume, dtype="float64")
    n = close.size
    out = np.full(n, np.nan)
    prev = 0.0
    for i in range(n):
        if i < period - 1:
            continue
        vsum = volume[i - period + 1 : i + 1].sum()
        if vsum == 0.0:
            out[i] = 0.0
            prev = 0.0
            continue
        x = (vsum - volume[i]) / vsum
        y = (volume[i] * close[i]) / vsum
        val = 0.0 if (x == 0.0 or y == 0.0) else prev * x + y
        out[i] = val
        prev = val
    return out


def test_evwma_warmup_is_period_minus_one():
    out = INDICATORS.create("evwma", period=20).compute(deterministic_frame(200))["evwma"]
    assert out.iloc[: 20 - 1].isna().all()  # one short of a full volume window -> NaN
    assert np.isfinite(out.iloc[20 - 1])  # first full window prints a real value


def test_evwma_first_value_is_y_seed():
    # Seeded from 0, the first full-window value is exactly y = volume*close / vsum.
    c = np.arange(1.0, 9.0)
    v = np.array([3.0, 5.0, 2.0, 7.0, 4.0, 6.0, 1.0, 8.0])
    period = 4
    out = INDICATORS.create("evwma", period=period).compute(frame(c, volume=v))["evwma"]
    vsum = v[:period].sum()
    expected_first = (v[period - 1] * c[period - 1]) / vsum  # prev=0 -> 0*x + y == y
    np.testing.assert_allclose(out.iloc[period - 1], expected_first, atol=1e-12)


def test_evwma_matches_recurrence_golden():
    # Bar-for-bar against the hand-rolled documented recurrence on an explicit small frame.
    c = np.array([10.0, 11.0, 9.0, 12.0, 13.0, 8.0, 14.0, 15.0, 7.0, 16.0])
    v = np.array([100.0, 120.0, 80.0, 200.0, 150.0, 90.0, 300.0, 110.0, 60.0, 250.0])
    period = 3
    out = INDICATORS.create("evwma", period=period).compute(frame(c, volume=v))["evwma"]
    np.testing.assert_allclose(out.to_numpy(), _golden(c, v, period), atol=1e-12, equal_nan=True)


def test_evwma_constant_converges_toward_close_from_below():
    # close=C, volume=V constant: EVWMA[i] = EVWMA[i-1]*(p-1)/p + C/p, seeded 0 -> rises to C.
    n, period, c_val = 200, 20, 50.0
    out = INDICATORS.create("evwma", period=period).compute(
        frame(np.full(n, c_val), volume=np.full(n, 1000.0))
    )["evwma"]
    v = out.dropna().to_numpy()
    assert (v < c_val + 1e-9).all()  # approaches the constant strictly from below
    assert np.all(np.diff(v) > 0)  # monotonically increasing toward it
    # Seed-from-0 convergence shrinks the gap by (p-1)/p per bar, so 200 bars lands ~5e-3 short.
    np.testing.assert_allclose(v[-1], c_val, atol=1e-2)  # converged toward C by the tail


def test_evwma_zero_volume_window_resets_to_zero():
    # Zero-volume full window -> vsum 0 -> finta resets the bar to 0 (post warm-up).
    n = 20
    df = frame(100.0 + np.arange(n, dtype="float64"), volume=np.zeros(n))
    out = INDICATORS.create("evwma", period=8).compute(df)["evwma"]
    post = out.iloc[8 - 1 :]
    assert (post == 0.0).all()


def test_evwma_short_frame_all_nan():
    out = INDICATORS.create("evwma", period=20).compute(frame([1.0, 2.0, 3.0]))["evwma"]
    assert out.isna().all()


def test_evwma_finite_and_varies_on_real_trend():
    out = INDICATORS.create("evwma", period=20).compute(deterministic_frame(300))["evwma"]
    v = out.dropna().to_numpy()
    assert v.size > 100 and np.isfinite(v).all() and v.std() > 0


def test_evwma_output_contract():
    df = deterministic_frame(60)
    res = INDICATORS.create("evwma", period=20).compute(df)
    assert list(res.columns) == ["evwma"]
    assert len(res) == len(df)
    assert str(res["evwma"].dtype) == "float64"
