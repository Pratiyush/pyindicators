"""DeMarker — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.momentum.demarker import demarker  # noqa: F401  (import fires @register)


def test_demarker_closed_form_matches_explicit_sma_loop():
    # Reconstruct DeM bar-by-bar from the explicit definition and require an exact match.
    df = deterministic_frame(120)
    out = INDICATORS.create("demarker", length=14).compute(df)["demarker"].to_numpy()
    high = df["high"].to_numpy()
    low = df["low"].to_numpy()
    de_max = np.maximum(np.diff(high, prepend=np.nan), 0.0)
    de_min = np.maximum(-np.diff(low, prepend=np.nan), 0.0)
    manual = np.full(high.shape, np.nan)
    for i in range(14, high.size):
        a = de_max[i - 13 : i + 1].mean()
        b = de_min[i - 13 : i + 1].mean()
        manual[i] = a / (a + b) if (a + b) != 0 else np.nan
    np.testing.assert_allclose(out, manual, rtol=1e-12, atol=1e-12, equal_nan=True)


def test_demarker_warmup_is_length_nans():
    # diff drops bar 0, so the first finite SMA (hence DeM) appears at index == length.
    out = INDICATORS.create("demarker", length=14).compute(deterministic_frame(120))["demarker"]
    assert out.iloc[:14].isna().all()
    assert out.iloc[14:].notna().all()
    assert out.first_valid_index() == 14


def test_demarker_bounded_zero_to_one():
    out = INDICATORS.create("demarker", length=14).compute(deterministic_frame(300))["demarker"]
    v = out.dropna().to_numpy()
    assert v.size > 200
    assert (v >= 0.0).all() and (v <= 1.0).all()


def test_demarker_pure_uptrend_is_one():
    # Every low is a higher low -> DeMin == 0 everywhere -> DeM == SMA(DeMax)/SMA(DeMax) == 1.
    n = 40
    high = np.arange(1.0, n + 1.0)
    low = high - 0.5
    out = INDICATORS.create("demarker", length=14).compute(frame(high, high=high, low=low))
    np.testing.assert_allclose(out["demarker"].dropna().to_numpy(), 1.0, rtol=0.0, atol=1e-12)


def test_demarker_pure_downtrend_is_zero():
    # Every high is a lower high -> DeMax == 0 everywhere -> DeM == 0/(0+SMA(DeMin)) == 0.
    n = 40
    high = np.arange(n + 1.0, 1.0, -1.0)
    low = high - 0.5
    out = INDICATORS.create("demarker", length=14).compute(frame(high, high=high, low=low))
    np.testing.assert_allclose(out["demarker"].dropna().to_numpy(), 0.0, rtol=0.0, atol=1e-12)


def test_demarker_flat_series_all_nan():
    # No higher highs and no lower lows -> SMA(DeMax) == SMA(DeMin) == 0 -> 0/0 -> NaN.
    flat = np.full(30, 100.0)
    out = INDICATORS.create("demarker", length=14).compute(frame(flat, high=flat, low=flat))
    assert out["demarker"].isna().all()


def test_demarker_short_frame_all_nan():
    out = INDICATORS.create("demarker", length=14).compute(frame([1.0, 2.0, 3.0]))["demarker"]
    assert out.isna().all()


def test_demarker_output_contract():
    out = INDICATORS.create("demarker", length=14).compute(deterministic_frame(60))
    assert list(out.columns) == ["demarker"]
    assert out["demarker"].dtype == np.float64
    assert len(out) == 60
