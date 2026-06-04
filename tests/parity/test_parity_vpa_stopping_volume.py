"""VPA Stopping Volume parity — GOLDEN-ONLY (no reference library implements this VSA pattern).

No TA-Lib / pandas-ta / finta / ta function computes "stopping volume", so there is no external
oracle. Instead the oracle here is the **closed-form four-condition definition itself**: this
file re-derives the flag independently with plain NumPy (an SMA via convolution, an explicit
close-location ratio) and asserts the indicator matches it bit-exactly on both the synthetic
``deterministic_frame()`` and genuine ``real_frame()`` AAPL bars. It also pins the structural
invariants (strictly 0/1, warm-up is 0 not NaN, fully causal).
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.volume import vpa_stopping_volume as _mod  # noqa: F401  (fires @register)

_TREND, _VOLN, _MULT, _LOC = 20, 20, 1.5, 0.5


def _trailing_sma(x: np.ndarray, n: int) -> np.ndarray:
    """Trailing mean over ``n`` bars (NaN until the window fills) — matches pandas rolling."""
    out = np.full(x.size, np.nan)
    if x.size >= n:
        csum = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1 :] = (csum[n:] - csum[:-n]) / n
    return out


def _reference(df) -> np.ndarray:
    """Independent NumPy re-implementation of the stopping-volume definition."""
    c = df["close"].to_numpy(dtype="float64")
    h = df["high"].to_numpy(dtype="float64")
    low = df["low"].to_numpy(dtype="float64")
    v = df["volume"].to_numpy(dtype="float64")

    downtrend = c < _trailing_sma(c, _TREND)
    prev_c = np.concatenate(([np.nan], c[:-1]))
    down_bar = c < prev_c
    high_vol = v > _MULT * _trailing_sma(v, _VOLN)
    rng = h - low
    with np.errstate(divide="ignore", invalid="ignore"):
        loc = np.where(rng == 0.0, np.nan, (c - low) / rng)
    off_low = loc >= _LOC  # NaN >= x is False

    hit = downtrend & down_bar & high_vol & off_low  # NaN comparisons -> False
    return np.where(hit, 1.0, 0.0)


def _ours(df) -> np.ndarray:
    out = INDICATORS.create(
        "vpa_stopping_volume",
        trend_length=_TREND,
        vol_length=_VOLN,
        vol_mult=_MULT,
        close_loc=_LOC,
    ).compute(df)["vpa_stopping_volume"]
    return out.to_numpy(dtype="float64")


def test_parity_synthetic_matches_closed_form():
    df = deterministic_frame()
    ours, ref = _ours(df), _reference(df)
    np.testing.assert_array_equal(ours, ref)
    assert ref.sum() > 0  # the synthetic walk actually triggers the pattern (test has teeth)


def test_parity_real_matches_closed_form():
    df = real_frame()  # genuine AAPL daily bars
    np.testing.assert_array_equal(_ours(df), _reference(df))


def test_structural_invariants_on_real_data():
    df = real_frame()
    ours = _ours(df)
    assert set(np.unique(ours)) <= {0.0, 1.0}  # strictly binary
    assert np.isfinite(ours).all()  # warm-up is 0, never NaN


def test_warmup_is_zero_not_nan():
    df = deterministic_frame()
    ours = _ours(df)
    # Before the 20-bar SMAs fill nothing can fire.
    assert (ours[: _TREND - 1] == 0.0).all()
    assert np.isfinite(ours).all()


def test_causal_truncation_invariance():
    # Recomputing on a prefix yields the same prefix values (no look-ahead).
    df = deterministic_frame()
    full = _ours(df)
    for k in (40, 150, len(df)):
        trunc = _ours(df.iloc[:k].copy())
        np.testing.assert_array_equal(full[:k], trunc)
