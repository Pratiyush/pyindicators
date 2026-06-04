"""STDERR (standard error of the OLS regression) — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.statistics.stderr import stderr  # import so @register fires


def _golden(close: np.ndarray, length: int) -> np.ndarray:
    """Independent oracle: per-window degree-1 ``np.polyfit`` residual std with ddof=2."""
    x = np.arange(length, dtype="float64")
    out = np.full(close.size, np.nan)
    for i in range(length - 1, close.size):
        w = close[i - length + 1 : i + 1]
        coef = np.polyfit(x, w, 1)
        resid = w - np.polyval(coef, x)
        out[i] = float(np.sqrt((resid * resid).sum() / (length - 2)))
    return out


def test_stderr_matches_per_window_ols_residual():
    df = deterministic_frame(200)
    close = df["close"].to_numpy()
    out = INDICATORS.create("stderr", length=14).compute(df)["stderr"]
    np.testing.assert_allclose(out.to_numpy(), _golden(close, 14), rtol=1e-9, atol=1e-9)
    # functional API matches the registry path exactly (and pins the @register import as used)
    np.testing.assert_allclose(stderr(df["close"], 14).to_numpy(), out.to_numpy(), atol=0.0)


def test_stderr_perfect_line_is_zero():
    # A perfectly straight line has zero residuals about its OLS fit -> stderr == 0 (exact fit).
    out = INDICATORS.create("stderr", length=14).compute(frame(np.arange(1.0, 50.0)))["stderr"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 0.0, atol=1e-9)


def test_stderr_perfect_downtrend_is_zero():
    out = INDICATORS.create("stderr", length=14).compute(
        frame(np.arange(50.0, 1.0, -1.0))
    )["stderr"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 0.0, atol=1e-9)


def test_stderr_flat_window_is_zero():
    # A flat window is also a perfect (zero-slope) fit -> zero residuals -> 0, not NaN.
    out = INDICATORS.create("stderr", length=14).compute(frame([7.0] * 40))["stderr"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 0.0, atol=1e-12)
    assert out.iloc[13:].notna().all()


def test_stderr_non_negative_on_real_walk():
    out = INDICATORS.create("stderr", length=14).compute(deterministic_frame(300))["stderr"]
    v = out.dropna().to_numpy()
    assert v.size > 200 and (v >= 0.0).all() and v.std() > 0.0


def test_stderr_short_frame_all_nan():
    out = INDICATORS.create("stderr", length=14).compute(frame([1.0, 2.0, 3.0]))["stderr"]
    assert out.isna().all()


def test_stderr_first_length_minus_one_nan():
    out = INDICATORS.create("stderr", length=10).compute(deterministic_frame(50))["stderr"]
    assert out.iloc[:9].isna().all() and out.iloc[9:].notna().any()
