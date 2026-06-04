"""MACDFIX — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.base import ema
from pyindicators.trend.macdfix import macdfix  # noqa: F401  (import fires @register)

# fast/slow are fixed at 12/26; first valid line at slow-1=25, first valid signal at 25+9-1=33.
_LINE_WARMUP = 26 - 1
_SIGNAL_WARMUP = _LINE_WARMUP + 9 - 1


def test_constant_series_is_zero():
    # EMA of a constant is the constant, so every output collapses to 0 past warm-up.
    out = INDICATORS.create("macdfix").compute(frame([7.0] * 60))
    assert list(out.columns) == ["macdfix", "macdfix_signal", "macdfix_hist"]
    np.testing.assert_allclose(out["macdfix"].dropna(), 0.0, atol=1e-12)
    np.testing.assert_allclose(out["macdfix_signal"].dropna(), 0.0, atol=1e-12)
    np.testing.assert_allclose(out["macdfix_hist"].dropna(), 0.0, atol=1e-12)


def test_matches_closed_form_ema_composition():
    # Golden: the indicator must equal the literal EMA(12)-EMA(26) / EMA(signal) composition.
    df = frame(np.arange(1.0, 120.0))
    out = INDICATORS.create("macdfix", signal=9).compute(df)
    line = ema(df["close"], 12, True) - ema(df["close"], 26, True)
    sig = ema(line, 9, True)
    np.testing.assert_allclose(out["macdfix"].to_numpy(), line.to_numpy(), equal_nan=True)
    np.testing.assert_allclose(out["macdfix_signal"].to_numpy(), sig.to_numpy(), equal_nan=True)
    np.testing.assert_allclose(
        out["macdfix_hist"].to_numpy(), (line - sig).to_numpy(), equal_nan=True
    )


def test_hist_is_line_minus_signal():
    out = INDICATORS.create("macdfix").compute(deterministic_frame(200))
    diff = (out["macdfix"] - out["macdfix_signal"]).to_numpy()
    np.testing.assert_allclose(out["macdfix_hist"].to_numpy(), diff, equal_nan=True)


def test_warmup_indices_and_length():
    out = INDICATORS.create("macdfix", signal=9).compute(frame(np.arange(1.0, 80.0)))
    assert len(out) == 79  # output length == input length
    assert out["macdfix"].iloc[:_LINE_WARMUP].isna().all()
    assert np.isfinite(out["macdfix"].iloc[_LINE_WARMUP])
    assert out["macdfix_signal"].iloc[:_SIGNAL_WARMUP].isna().all()
    assert np.isfinite(out["macdfix_signal"].iloc[_SIGNAL_WARMUP])


def test_short_frame_all_nan():
    # Fewer than slow (26) bars -> the line never seeds, so everything is NaN.
    out = INDICATORS.create("macdfix").compute(frame(np.arange(1.0, 20.0)))
    assert out["macdfix"].isna().all()
    assert out["macdfix_signal"].isna().all()
    assert out["macdfix_hist"].isna().all()


def test_outputs_finite_and_float64_on_real_trend():
    out = INDICATORS.create("macdfix").compute(deterministic_frame(300))
    assert list(out.columns) == ["macdfix", "macdfix_signal", "macdfix_hist"]
    assert all(str(out[c].dtype) == "float64" for c in out.columns)
    assert np.isfinite(out.iloc[-1].to_numpy()).all()


def test_signal_period_configurable():
    # A longer signal smooths more -> later first-valid index and lower tail variance.
    df = deterministic_frame(300)
    fast_sig = INDICATORS.create("macdfix", signal=5).compute(df)["macdfix_signal"]
    slow_sig = INDICATORS.create("macdfix", signal=20).compute(df)["macdfix_signal"]
    assert np.flatnonzero(np.isfinite(slow_sig.to_numpy()))[0] > np.flatnonzero(
        np.isfinite(fast_sig.to_numpy())
    )[0]
    assert slow_sig.dropna().std() < fast_sig.dropna().std()
