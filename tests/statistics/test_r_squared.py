"""R-Squared (coefficient of determination) — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.statistics.r_squared import r_squared  # import so @register fires


def _golden(close: np.ndarray, length: int) -> np.ndarray:
    """Independent oracle: square of np.corrcoef(window, arange) per trailing window."""
    x = np.arange(length, dtype="float64")
    out = np.full(close.size, np.nan)
    for i in range(length - 1, close.size):
        w = close[i - length + 1 : i + 1]
        if np.ptp(w) == 0.0:  # flat window -> correlation undefined
            continue
        out[i] = float(np.corrcoef(x, w)[0, 1]) ** 2
    return out


def test_r_squared_matches_closed_form():
    df = deterministic_frame(200)
    close = df["close"].to_numpy()
    out = INDICATORS.create("r_squared", length=14).compute(df)["r_squared"]
    np.testing.assert_allclose(out.to_numpy(), _golden(close, 14), rtol=1e-9, atol=1e-9)
    # functional API matches the registry path exactly (and pins the @register import as used)
    np.testing.assert_allclose(r_squared(df["close"], 14).to_numpy(), out.to_numpy(), atol=0.0)


def test_r_squared_perfect_line_is_one():
    # A perfectly straight line (any slope) is fully explained by the regression -> r^2 == 1.
    out = INDICATORS.create("r_squared", length=14).compute(frame(np.arange(1.0, 50.0)))["r_squared"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 1.0, atol=1e-12)


def test_r_squared_perfect_downtrend_is_one():
    out = INDICATORS.create("r_squared", length=14).compute(
        frame(np.arange(50.0, 1.0, -1.0))
    )["r_squared"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 1.0, atol=1e-12)


def test_r_squared_bounds_zero_to_one():
    out = INDICATORS.create("r_squared", length=14).compute(deterministic_frame(300))["r_squared"]
    v = out.dropna().to_numpy()
    assert v.size > 200
    assert v.min() >= 0.0 - 1e-12 and v.max() <= 1.0 + 1e-12


def test_r_squared_flat_window_is_nan():
    out = INDICATORS.create("r_squared", length=14).compute(frame([7.0] * 40))["r_squared"]
    assert out.isna().all()  # zero price variance -> r undefined -> NaN, not 0 or 1


def test_r_squared_short_frame_all_nan():
    out = INDICATORS.create("r_squared", length=14).compute(frame([1.0, 2.0, 3.0]))["r_squared"]
    assert out.isna().all()


def test_r_squared_first_length_minus_one_nan():
    out = INDICATORS.create("r_squared", length=10).compute(deterministic_frame(50))["r_squared"]
    assert out.iloc[:9].isna().all() and out.iloc[9:].notna().any()
