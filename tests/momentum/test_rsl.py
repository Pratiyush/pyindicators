"""Relative Strength Levy (close / SMA) — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.base import sma
from pyindicators.momentum.rsl import rsl  # noqa: F401  (import fires @register)


def test_rsl_closed_form_matches_close_over_sma():
    # RSL is exactly close / SMA(close, length) by definition.
    df = deterministic_frame(200)
    out = INDICATORS.create("rsl", length=26).compute(df)["rsl"]
    expected = df["close"] / sma(df["close"], 26)
    np.testing.assert_allclose(out.to_numpy(), expected.to_numpy(), rtol=1e-12, atol=1e-12)


def test_rsl_constant_series_is_one():
    # A flat series equals its own SMA, so the ratio is exactly 1.0 once warmed up.
    out = INDICATORS.create("rsl", length=5).compute(frame([7.0] * 12))["rsl"]
    v = out.dropna().to_numpy()
    assert v.size == 8  # 12 bars - (length-1) warm-up
    np.testing.assert_allclose(v, 1.0, rtol=0.0, atol=1e-12)


def test_rsl_warmup_is_nan():
    # First length-1 bars are NaN (SMA warm-up); the length-th bar is finite.
    out = INDICATORS.create("rsl", length=4).compute(frame([1.0, 2.0, 3.0, 4.0, 5.0]))["rsl"]
    assert out.iloc[:3].isna().all()
    assert np.isfinite(out.iloc[3])


def test_rsl_above_one_when_price_leads_average():
    # On a rising series the latest close sits above its trailing mean -> RSL > 1.
    out = INDICATORS.create("rsl", length=5).compute(frame(np.arange(1.0, 30.0)))["rsl"]
    v = out.dropna().to_numpy()
    assert (v > 1.0).all()


def test_rsl_below_one_when_price_lags_average():
    # On a falling series the latest close sits below its trailing mean -> RSL < 1.
    out = INDICATORS.create("rsl", length=5).compute(frame(np.arange(30.0, 1.0, -1.0)))["rsl"]
    v = out.dropna().to_numpy()
    assert (v < 1.0).all()


def test_rsl_short_frame_all_nan():
    out = INDICATORS.create("rsl", length=26).compute(frame([1.0, 2.0, 3.0]))["rsl"]
    assert out.isna().all()


def test_rsl_zero_basis_guarded_to_nan():
    # A flat window at price 0 -> SMA == 0 -> 0/0 is guarded to NaN, not +/-inf.
    out = INDICATORS.create("rsl", length=3).compute(frame([0.0, 0.0, 0.0, 0.0]))["rsl"]
    finite = out.dropna()
    assert finite.empty  # every warmed-up bar divides by a zero basis -> NaN
    assert not np.isinf(out.to_numpy()).any()


def test_rsl_output_contract():
    df = deterministic_frame(60)
    out = INDICATORS.create("rsl", length=26).compute(df)
    assert list(out.columns) == ["rsl"]
    assert out["rsl"].dtype == np.float64
    assert len(out) == len(df)


def test_rsl_default_length_is_26():
    df = deterministic_frame(60)
    default = INDICATORS.create("rsl").compute(df)["rsl"]
    explicit = INDICATORS.create("rsl", length=26).compute(df)["rsl"]
    np.testing.assert_allclose(default.to_numpy(), explicit.to_numpy(), rtol=0.0, atol=0.0)
