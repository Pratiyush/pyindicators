"""MACDEXT (SMA-mode) — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.base import sma
from pyindicators.trend.macdext import macdext  # noqa: F401  (import fires @register)

# Default fast/slow/signal = 12/26/9. The line seeds at slow-1=25; the SMA-of-line signal
# needs another full window, so it first seeds at 25 + (9-1) = 33.
_LINE_WARMUP = 26 - 1
_SIGNAL_WARMUP = _LINE_WARMUP + 9 - 1


def test_constant_series_is_zero():
    # SMA of a constant is the constant, so every output collapses to 0 past warm-up.
    out = INDICATORS.create("macdext").compute(frame([7.0] * 60))
    assert list(out.columns) == ["macdext", "macdext_signal", "macdext_hist"]
    np.testing.assert_allclose(out["macdext"].dropna(), 0.0, atol=1e-12)
    np.testing.assert_allclose(out["macdext_signal"].dropna(), 0.0, atol=1e-12)
    np.testing.assert_allclose(out["macdext_hist"].dropna(), 0.0, atol=1e-12)


def test_matches_closed_form_sma_composition():
    # Golden: the indicator must equal the literal SMA(12)-SMA(26) / SMA(line,9) composition.
    df = frame(np.arange(1.0, 120.0))
    out = INDICATORS.create("macdext", fast=12, slow=26, signal=9).compute(df)
    line = sma(df["close"], 12) - sma(df["close"], 26)
    sig = sma(line, 9)
    np.testing.assert_allclose(out["macdext"].to_numpy(), line.to_numpy(), equal_nan=True)
    np.testing.assert_allclose(out["macdext_signal"].to_numpy(), sig.to_numpy(), equal_nan=True)
    np.testing.assert_allclose(
        out["macdext_hist"].to_numpy(), (line - sig).to_numpy(), equal_nan=True
    )


def test_line_on_linear_ramp_is_constant_gap():
    # On a unit-slope ramp, SMA(c,n) lags the value by (n-1)/2, so the line is a constant
    # (slow-fast)/2 = (26-12)/2 = 7 once both SMAs have seeded.
    out = INDICATORS.create("macdext").compute(frame(np.arange(1.0, 200.0)))
    np.testing.assert_allclose(out["macdext"].dropna().to_numpy(), 7.0, atol=1e-9)


def test_hist_is_line_minus_signal():
    out = INDICATORS.create("macdext").compute(deterministic_frame(200))
    diff = (out["macdext"] - out["macdext_signal"]).to_numpy()
    np.testing.assert_allclose(out["macdext_hist"].to_numpy(), diff, equal_nan=True)


def test_warmup_indices_and_length():
    out = INDICATORS.create("macdext", signal=9).compute(frame(np.arange(1.0, 80.0)))
    assert len(out) == 79  # output length == input length
    assert out["macdext"].iloc[:_LINE_WARMUP].isna().all()
    assert np.isfinite(out["macdext"].iloc[_LINE_WARMUP])
    assert out["macdext_signal"].iloc[:_SIGNAL_WARMUP].isna().all()
    assert np.isfinite(out["macdext_signal"].iloc[_SIGNAL_WARMUP])


def test_short_frame_all_nan():
    # Fewer than slow (26) bars -> the line never seeds, so everything is NaN.
    out = INDICATORS.create("macdext").compute(frame(np.arange(1.0, 20.0)))
    assert out["macdext"].isna().all()
    assert out["macdext_signal"].isna().all()
    assert out["macdext_hist"].isna().all()


def test_outputs_finite_and_float64_on_real_trend():
    out = INDICATORS.create("macdext").compute(deterministic_frame(300))
    assert list(out.columns) == ["macdext", "macdext_signal", "macdext_hist"]
    assert all(str(out[c].dtype) == "float64" for c in out.columns)
    assert np.isfinite(out.iloc[-1].to_numpy()).all()


def test_signal_period_configurable():
    # A longer signal smooths more -> later first-valid index and lower tail variance.
    df = deterministic_frame(300)
    fast_sig = INDICATORS.create("macdext", signal=5).compute(df)["macdext_signal"]
    slow_sig = INDICATORS.create("macdext", signal=20).compute(df)["macdext_signal"]
    assert np.flatnonzero(np.isfinite(slow_sig.to_numpy()))[0] > np.flatnonzero(
        np.isfinite(fast_sig.to_numpy())
    )[0]
    assert slow_sig.dropna().std() < fast_sig.dropna().std()
