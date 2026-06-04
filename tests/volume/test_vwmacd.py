"""Volume-Weighted MACD (finta EV_MACD) — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.volume.vwmacd import evwma, vwmacd  # noqa: F401  (import fires @register)


def _evwma_oracle(close, volume, period):
    """Independent re-derivation of finta's EVWMA recurrence (the contract under test)."""
    c = np.asarray(close, dtype="float64")
    v = np.asarray(volume, dtype="float64")
    out = np.empty(c.size, dtype="float64")
    prev = 0.0
    for i in range(c.size):
        if i < period - 1:
            out[i] = 0.0  # rolling warm-up -> finta emits 0, not NaN
            prev = 0.0
            continue
        vol_sum = v[i - period + 1 : i + 1].sum()
        x = 0.0 if vol_sum == 0 else (vol_sum - v[i]) / vol_sum
        y = np.nan if vol_sum == 0 else (v[i] * c[i]) / vol_sum
        if x == 0.0 or y == 0.0:
            prev = 0.0
        else:
            prev = prev * x + y
        out[i] = prev
    return out


def test_outputs_shape_and_columns():
    df = deterministic_frame(120)
    out = INDICATORS.create("vwmacd").compute(df)
    assert list(out.columns) == ["vwmacd", "vwmacd_signal"]
    assert len(out) == len(df)
    assert str(out["vwmacd"].dtype) == "float64"


def test_evwma_matches_closed_form_recurrence():
    # Lock the EVWMA recurrence (and its 0-warm-up) against an independent re-derivation.
    df = deterministic_frame(150)
    for period in (12, 26):
        got = evwma(df["close"], df["volume"], period).to_numpy()
        want = _evwma_oracle(df["close"], df["volume"], period)
        np.testing.assert_allclose(got, want, rtol=1e-12, atol=1e-12)


def test_constant_series_converges_to_zero():
    # Constant close & volume -> both EVWMAs converge to the constant -> line/signal -> 0.
    # Convergence is geometric (ratio (period-1)/period); 1000 bars reaches float precision.
    c = np.full(1000, 50.0)
    v = np.full(1000, 1000.0)
    df = frame(c, volume=v)
    out = INDICATORS.create("vwmacd", fast=12, slow=26, signal=9).compute(df)
    assert abs(out["vwmacd"].iloc[-1]) < 1e-9
    assert abs(out["vwmacd_signal"].iloc[-1]) < 1e-9
    # each EVWMA itself converges to the constant price paid per share
    np.testing.assert_allclose(evwma(df["close"], df["volume"], 26).iloc[-1], 50.0, atol=1e-9)


def test_zero_volume_window_resets_to_zero():
    # finta resets the recurrence to 0 on any window whose volume contributions zero out.
    c = np.arange(1.0, 21.0)
    v = np.full(20, 1000.0)
    v[10:16] = 0.0  # a zero-volume block wider than the period
    ev = evwma(frame(c, volume=v)["close"], frame(c, volume=v)["volume"], 5)
    # bars whose 5-wide window is entirely inside the zero block must be exactly 0
    assert ev.iloc[13] == 0.0
    assert ev.iloc[14] == 0.0


def test_short_frame_all_zero_warmup():
    # Fewer bars than fast(12): every bar is in warm-up -> finta-style 0 fill (not NaN).
    df = frame(np.arange(1.0, 6.0), volume=[100.0, 200.0, 300.0, 400.0, 500.0])
    out = INDICATORS.create("vwmacd", fast=12, slow=26, signal=9).compute(df)
    assert (out["vwmacd"].to_numpy() == 0.0).all()
    assert (out["vwmacd_signal"].to_numpy() == 0.0).all()


def test_line_finite_and_varies_on_real_trend():
    out = INDICATORS.create("vwmacd").compute(deterministic_frame(300))
    line = out["vwmacd"].to_numpy()
    assert np.isfinite(line).all()
    assert line[50:].std() > 0  # genuinely moves once past the warm-up
