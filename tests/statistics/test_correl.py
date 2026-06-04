"""CORREL — rolling Pearson correlation: golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.statistics.correl import correl  # noqa: F401 — registers @INDICATORS


def test_correl_perfectly_correlated_window_is_one():
    # high and low move in lockstep (low = 2*high) -> r = 1 on every full window.
    hi = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    lo = 2.0 * hi
    out = INDICATORS.create("correl", length=3).compute(frame(hi, high=hi, low=lo))["correl"]
    np.testing.assert_allclose(out.iloc[2:].to_numpy(), 1.0, atol=1e-12)


def test_correl_perfectly_anticorrelated_window_is_minus_one():
    hi = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    lo = -hi
    out = INDICATORS.create("correl", length=3).compute(frame(hi, high=hi, low=lo))["correl"]
    np.testing.assert_allclose(out.iloc[2:].to_numpy(), -1.0, atol=1e-12)


def test_correl_closed_form_window():
    # Pearson r over the trailing 3-bar window, computed by hand (sum-form).
    hi = np.array([2.0, 3.0, 10.0])
    lo = np.array([4.0, 6.0, 1.0])
    n = 3
    num = n * (hi * lo).sum() - hi.sum() * lo.sum()
    den = np.sqrt((n * (hi * hi).sum() - hi.sum() ** 2) * (n * (lo * lo).sum() - lo.sum() ** 2))
    expected = num / den
    out = INDICATORS.create("correl", length=3).compute(frame(hi, high=hi, low=lo))["correl"]
    np.testing.assert_allclose(out.iloc[-1], expected, atol=1e-12)


def test_correl_flat_window_is_nan():
    # Zero variance in one input -> correlation undefined (0/0) -> NaN (library convention).
    hi = np.array([5.0] * 8)  # flat high
    lo = np.arange(8.0)
    out = INDICATORS.create("correl", length=4).compute(frame(hi, high=hi, low=lo))["correl"]
    assert out.iloc[3:].isna().all()


def test_correl_short_frame_all_nan():
    out = INDICATORS.create("correl", length=30).compute(frame([1.0, 2.0, 3.0]))["correl"]
    assert out.isna().all()


def test_correl_warmup_then_finite_and_bounded():
    out = INDICATORS.create("correl", length=30).compute(deterministic_frame(200))["correl"]
    assert out.iloc[:29].isna().all()  # length-1 warm-up
    v = out.dropna().to_numpy()
    assert v.size > 100
    assert ((v >= -1.0) & (v <= 1.0)).all()  # clamped into [-1, 1]
