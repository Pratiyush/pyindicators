"""STARC Bands — golden / closed-form + edge cases.

STARC = SMA(close, ma_length) +/- mult * ATR(atr_length). The middle is a plain SMA (so it
matches our base SMA exactly) and the half-width is ``mult * ATR``; everything else follows
from those two composed primitives.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.base import sma
from pyindicators.volatility.atr import atr  # noqa: F401  (import fires @register for self-test)
from pyindicators.volatility.starc import starc  # noqa: F401  (registers "starc")

MA, ATRN, MULT = 5, 15, 2.0


def _starc(df, ma_length=MA, atr_length=ATRN, mult=MULT):
    return INDICATORS.create(
        "starc", ma_length=ma_length, atr_length=atr_length, mult=mult
    ).compute(df)


def test_output_contract():
    out = _starc(deterministic_frame(120))
    assert list(out.columns) == ["starc_middle", "starc_upper", "starc_lower"]
    assert len(out) == 120
    assert all(out[c].dtype == np.float64 for c in out.columns)


def test_middle_is_exactly_sma():
    # The basis is a *simple* MA (the defining difference from Keltner's EMA), so it must equal
    # our base SMA bit-for-bit on any frame.
    df = deterministic_frame(200)
    out = _starc(df)
    np.testing.assert_array_equal(
        out["starc_middle"].to_numpy(), sma(df["close"], MA).to_numpy()
    )


def test_bands_are_symmetric_about_middle():
    # upper - middle == middle - lower == mult * ATR (FP non-associativity of (m+b)-m allows
    # only a ~1e-15 wobble, hence the tiny rtol rather than exact equality).
    df = deterministic_frame(200)
    out = _starc(df)
    half = MULT * atr(df, ATRN)
    np.testing.assert_allclose((out["starc_upper"] - out["starc_middle"]).to_numpy(),
                               half.to_numpy(), equal_nan=True, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose((out["starc_middle"] - out["starc_lower"]).to_numpy(),
                               half.to_numpy(), equal_nan=True, rtol=1e-12, atol=1e-12)
    # Ordering once finite: lower <= middle <= upper (ATR >= 0).
    m = out.dropna()
    assert (m["starc_lower"] <= m["starc_middle"] + 1e-12).all()
    assert (m["starc_middle"] <= m["starc_upper"] + 1e-12).all()


def test_constant_series_collapses_bands_to_sma():
    # H == L == C => TR == 0 => ATR == 0 => all three lines equal the (constant) SMA.
    n = 60
    c = np.full(n, 42.0)
    out = _starc(frame(c))
    valid = out.dropna()
    assert len(valid) == n - max(MA, ATRN) + 1
    np.testing.assert_allclose(valid["starc_middle"].to_numpy(), 42.0)
    np.testing.assert_allclose(valid["starc_upper"].to_numpy(), 42.0)
    np.testing.assert_allclose(valid["starc_lower"].to_numpy(), 42.0)


def test_closed_form_constant_true_range():
    # Construct TR == r on every bar: close constant = c, high = c + a, low = c - b with
    # a + b = r. Then H-L = r and both gaps (|H-prevC|=a, |L-prevC|=b) are <= r, so TR = r.
    # ATR (Wilder mean of a constant) == r everywhere it is defined => half-width = mult*r.
    n, c, a, b = 80, 100.0, 0.7, 0.5
    r = a + b
    close = np.full(n, c)
    high = np.full(n, c + a)
    low = np.full(n, c - b)
    out = _starc(frame(close, high=high, low=low))
    valid = out.dropna()
    np.testing.assert_allclose(valid["starc_middle"].to_numpy(), c)
    np.testing.assert_allclose(valid["starc_upper"].to_numpy(), c + MULT * r)
    np.testing.assert_allclose(valid["starc_lower"].to_numpy(), c - MULT * r)


def test_short_frame_bands_nan_middle_may_warm():
    # Warm-ups are independent: a 5-bar frame clears the SMA (ma_length=5) but not the ATR
    # (atr_length=15), so the middle has exactly one value and BOTH bands stay all-NaN.
    out = _starc(frame(np.arange(1.0, 6.0)))  # 5 bars: >= ma_length, < atr_length
    assert out["starc_upper"].isna().all()
    assert out["starc_lower"].isna().all()
    assert out["starc_middle"].notna().sum() == 1  # SMA(5) of 5 bars -> last bar only


def test_tiny_frame_all_nan():
    # Fewer bars than EITHER window => nothing is defined anywhere.
    out = _starc(frame(np.arange(1.0, 4.0)))  # 3 bars < ma_length and < atr_length
    assert out.isna().all().all()


def test_warmup_governed_by_longer_window():
    # First finite band row is at index max(ma_length, atr_length) - 1.
    df = deterministic_frame(120)
    out = _starc(df, ma_length=5, atr_length=15)
    first = out["starc_upper"].first_valid_index()
    assert first == max(5, 15) - 1
    assert out["starc_upper"].iloc[:first].isna().all()


def test_mult_scales_bandwidth_linearly():
    # Doubling mult doubles the distance from the middle (ATR/SMA unchanged).
    df = deterministic_frame(150)
    o1 = _starc(df, mult=1.0)
    o2 = _starc(df, mult=2.0)
    d1 = (o1["starc_upper"] - o1["starc_middle"]).dropna().to_numpy()
    d2 = (o2["starc_upper"] - o2["starc_middle"]).dropna().to_numpy()
    np.testing.assert_allclose(d2, 2.0 * d1, rtol=1e-12)
