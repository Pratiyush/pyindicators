"""Big Shadow "parity" — structural / closed-form invariants (GOLDEN-ONLY, no oracle).

No reference library (TA-Lib, pandas-ta, finta, ``ta``) implements Big Shadow, so there is
nothing to compare against. Instead this file pins the *definition* by re-deriving it
independently and asserting it holds on both ``deterministic_frame()`` and the real AAPL
fixture: every fired bar must (a) range-engulf its predecessor, (b) be wider than
``factor`` * trailing-average-range, and (c) carry the sign of its candle colour; every
non-fired bar must violate at least one of those. Output is always in {-100, 0, 100}.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.big_shadow import big_shadow  # noqa: F401  (import fires @register)

_PERIOD = 10
_FACTOR = 2.0


def _reference(df: pd.DataFrame) -> np.ndarray:
    """Independent re-derivation of Big Shadow straight from the OHLC arrays."""
    o = df["open"].to_numpy("float64")
    h = df["high"].to_numpy("float64")
    low = df["low"].to_numpy("float64")
    c = df["close"].to_numpy("float64")
    rng = h - low
    avg = pd.Series(rng).shift(1).rolling(_PERIOD, min_periods=_PERIOD).mean().to_numpy()
    prev_h = pd.Series(h).shift(1).to_numpy()
    prev_l = pd.Series(low).shift(1).to_numpy()
    engulf = (h > prev_h) & (low < prev_l)
    wide = rng > _FACTOR * avg
    color = np.where(c >= o, 1.0, -1.0)
    out = np.where(engulf & wide, color * 100.0, 0.0)
    out[:_PERIOD] = 0.0
    return out


def _check(df: pd.DataFrame) -> np.ndarray:
    out = INDICATORS.create(
        "big_shadow", avg_period=_PERIOD, factor=_FACTOR
    ).compute(df)["big_shadow"].to_numpy()
    # Output domain.
    assert set(np.unique(out)).issubset({-100.0, 0.0, 100.0})
    # Matches the independent re-derivation exactly (integer outputs, no tolerance).
    np.testing.assert_array_equal(out, _reference(df))
    # Warm-up is always zero.
    np.testing.assert_array_equal(out[:_PERIOD], 0.0)
    return out


def test_big_shadow_structure_synthetic():
    df = deterministic_frame()
    out = _check(df)
    # Each fired bar genuinely range-engulfs its predecessor and is a wide bar.
    h = df["high"].to_numpy()
    low = df["low"].to_numpy()
    rng = h - low
    avg = pd.Series(rng).shift(1).rolling(_PERIOD, min_periods=_PERIOD).mean().to_numpy()
    fired = np.flatnonzero(out != 0.0)
    for i in fired:
        assert h[i] > h[i - 1] and low[i] < low[i - 1]  # range-engulf
        assert rng[i] > _FACTOR * avg[i]  # wide
    assert fired.size > 0  # the synthetic walk does produce some Big Shadows


def test_big_shadow_sign_follows_color_real():
    df = real_frame()  # genuine AAPL daily bars
    out = _check(df)
    o = df["open"].to_numpy()
    c = df["close"].to_numpy()
    fired = np.flatnonzero(out != 0.0)
    for i in fired:
        expected = 100.0 if c[i] >= o[i] else -100.0
        assert out[i] == expected


def test_big_shadow_causal_on_slice():
    # Causality: a prefix of the full output equals the indicator recomputed on the prefix.
    df = deterministic_frame()
    full = INDICATORS.create("big_shadow").compute(df)["big_shadow"].to_numpy()
    k = 137
    head = INDICATORS.create("big_shadow").compute(df.iloc[:k].copy())["big_shadow"].to_numpy()
    np.testing.assert_array_equal(full[:k], head)
