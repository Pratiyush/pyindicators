"""Breakaway parity — EXACT integer match vs ``talib.CDLBREAKAWAY`` (synthetic + real).

CDLBREAKAWAY is a rare five-candle pattern, so the synthetic walk and the AAPL fixture are
both all-zero — those frames pin "no false positives". To prove the *positive* path matches
TA-Lib bit-exactly we also assert on two hand-built breakaway frames (one of each sign) and a
deterministic boundary fuzz that produces thousands of genuine hits of both signs.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.breakaway import breakaway  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")

_LOOKBACK = 14


def _ohlc(df):
    return tuple(df[col].to_numpy(dtype="float64") for col in ("open", "high", "low", "close"))


def _our(df):
    return INDICATORS.create("breakaway").compute(df)["breakaway"].to_numpy()


def _ref(df):
    return talib.CDLBREAKAWAY(*_ohlc(df)).astype("float64")


def _check(df):
    our = _our(df)
    ref = _ref(df)
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_breakaway_parity_synthetic():
    _check(deterministic_frame())


def test_breakaway_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_breakaway_parity_gap_up_structure():
    # Gap-up (white-tendency) five-bar breakaway; fifth candle black -> TA-Lib emits -100.
    o = [100.0] * 10 + [100.0, 114.0, 117.0, 120.0, 124.0]
    c = [100.5] * 10 + [112.0, 116.0, 119.0, 123.0, 113.0]
    h = [100.7] * 10 + [112.5, 116.5, 119.5, 123.5, 124.5]
    low = [99.9] * 10 + [99.5, 113.5, 116.5, 119.5, 112.5]
    df = frame(c, high=h, low=low, open_=o)
    assert _ref(df)[14] == -100.0  # guard: the fixture really is a breakaway
    _check(df)


def test_breakaway_parity_gap_down_structure():
    # Gap-down (black-tendency) five-bar breakaway; fifth candle white -> TA-Lib emits +100.
    o = [100.0] * 10 + [112.0, 98.0, 95.0, 92.0, 88.0]
    c = [99.5] * 10 + [100.0, 96.0, 93.0, 90.0, 99.0]
    h = [100.1] * 10 + [112.5, 98.5, 95.5, 92.5, 99.5]
    low = [99.3] * 10 + [99.5, 95.5, 92.5, 89.5, 87.5]
    df = frame(c, high=h, low=low, open_=o)
    assert _ref(df)[14] == 100.0  # guard: the fixture really is a breakaway
    _check(df)


def _boundary_frame(rng, bullish):
    """A 15-bar frame jittered around a valid breakaway template (boundaries get stressed)."""
    o = np.zeros(15)
    c = np.zeros(15)
    h = np.zeros(15)
    low = np.zeros(15)
    sign = 1.0 if bullish else -1.0  # bullish == gap-up white tendency
    for k in range(10):  # small warm-up bodies in the trend direction
        o[k] = 100.0 + rng.normal(0, 0.3)
        c[k] = o[k] + sign * abs(rng.normal(0.4, 0.2))
        h[k] = max(o[k], c[k]) + abs(rng.normal(0, 0.2))
        low[k] = min(o[k], c[k]) - abs(rng.normal(0, 0.2))
    o[10] = (100.0 if bullish else 112.0) + rng.normal(0, 0.5)
    c[10] = o[10] + sign * abs(rng.normal(12, 3))
    h[10] = max(o[10], c[10]) + abs(rng.normal(0, 0.3))
    low[10] = min(o[10], c[10]) - abs(rng.normal(0, 0.3))
    gap = rng.normal(2, 2)  # sometimes negative -> kills the gap (a true negative)
    o[11] = c[10] + sign * gap
    c[11] = o[11] + sign * abs(rng.normal(2, 1))
    h[11] = max(o[11], c[11]) + abs(rng.normal(0, 0.3))
    low[11] = min(o[11], c[11]) - abs(rng.normal(0, 0.3))
    for k in (12, 13):  # continue the trend; jitter highs/lows across the strict boundary
        o[k] = c[k - 1] + sign * rng.normal(1, 1)
        c[k] = o[k] + sign * abs(rng.normal(2, 1))
        h[k] = h[k - 1] + sign * rng.normal(1, 1.5)
        low[k] = low[k - 1] + sign * rng.normal(1, 1.5)
    o[14] = c[13] + sign * rng.normal(2, 2)  # 5th candle, opposite colour by construction
    target = (o[11] + c[10]) / 2 + rng.normal(0, 2)  # aim the close into the gap, jittered
    c[14] = target
    h[14] = max(o[14], c[14]) + abs(rng.normal(0, 0.3))
    low[14] = min(o[14], c[14]) - abs(rng.normal(0, 0.3))
    return frame(c, high=h, low=low, open_=o)


def test_breakaway_parity_boundary_fuzz():
    # Thousands of near-boundary frames of both signs: TA-Lib and ours must agree bit-for-bit,
    # and the corpus must contain genuine hits of *both* signs (so the positive path is tested).
    rng = np.random.default_rng(7)
    pos = neg = 0
    for t in range(6000):
        df = _boundary_frame(rng, bullish=(t % 2 == 0))
        our = _our(df)
        ref = _ref(df)
        np.testing.assert_array_equal(our, ref)
        pos += int(np.count_nonzero(ref > 0))
        neg += int(np.count_nonzero(ref < 0))
    assert pos > 0 and neg > 0  # both the +100 and -100 paths were exercised


def test_breakaway_lookback_is_zero():
    # The first ``lookback`` bars are forced to 0 to match TA-Lib.
    df = deterministic_frame()
    np.testing.assert_array_equal(_our(df)[:_LOOKBACK], 0.0)
