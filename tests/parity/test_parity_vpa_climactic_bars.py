"""VPA Climactic Bars parity — closed-form / structural (no reference library oracle).

No talib / pandas-ta / finta / ta function computes a VSA "climax" bar, so there is nothing to
import for a numeric oracle. Instead this re-derives the documented closed-form rule a second,
independent way (plain ``rolling`` means + a strict prior-window extreme via ``shift``) and
asserts the indicator matches it EXACTLY on both the deterministic frame and genuine AAPL
daily bars, and that the rule actually fires on real data. This is the structural analogue of
the candle parity tests, kept under ``tests/parity/`` per the build convention.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.volume.vpa_climactic_bars import (  # noqa: F401  (import fires @register)
    vpa_climactic_bars,
)


def _reference(df: pd.DataFrame, length: int, vol_k: float, range_k: float) -> np.ndarray:
    """Independent closed-form re-derivation of the VSA climax flag (Williams / Coulling)."""
    close, high, low, vol = (df[c] for c in ("close", "high", "low", "volume"))
    rng = high - low

    vol_avg = vol.rolling(length, min_periods=length).mean()
    rng_avg = rng.rolling(length, min_periods=length).mean()
    ultra_vol = vol > vol_k * vol_avg
    wide = rng > range_k * rng_avg

    prior = close.shift(1)
    new_high = close > prior.rolling(length, min_periods=length).max()
    new_low = close < prior.rolling(length, min_periods=length).min()

    return (ultra_vol & wide & (new_high | new_low)).astype("float64").to_numpy()


def _check(df: pd.DataFrame, **kw) -> np.ndarray:
    length = kw.get("length", 20)
    vol_k = kw.get("vol_k", 2.0)
    range_k = kw.get("range_k", 1.5)
    our = INDICATORS.create("vpa_climactic_bars", **kw).compute(df)[
        "vpa_climactic_bars"
    ].to_numpy()
    ref = _reference(df, length, vol_k, range_k)
    assert our.shape == ref.shape
    np.testing.assert_array_equal(our, ref)  # exact: a 0/1 flag, no tolerance
    assert np.isfinite(our).all()  # finite everywhere (warm-up is 0, never NaN)
    assert set(np.unique(our)) <= {0.0, 1.0}
    return our


def test_vpa_climactic_bars_parity_synthetic():
    df = deterministic_frame()
    _check(df)  # defaults: the smooth synthetic walk rarely (here never) hits a climax
    # Loosened thresholds DO fire on the synthetic frame, so the exact-equality cross-check
    # below is non-trivial (compares two independent derivations on a mix of 0s and 1s).
    fired = _check(df, length=10, vol_k=1.05, range_k=1.0)
    assert fired.sum() > 0


def test_vpa_climactic_bars_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    # Loosen the thresholds so the rule demonstrably fires on the real fixture, then confirm
    # the indicator reproduces the independent closed form exactly on real price action.
    out = _check(df, length=20, vol_k=1.5, range_k=1.1)
    assert out.sum() > 0  # at least one real climactic bar is detected
